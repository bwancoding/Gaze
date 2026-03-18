"""
JWT Authentication API
用户认证和 Token 管理
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

limiter = Limiter(key_func=get_remote_address)

from app.core.database import get_db
from app.models import User
from app.utils.security import verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# JWT 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is required. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 天

# Bearer Token 认证
security = HTTPBearer()


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token 中的数据"""
    user_id: Optional[str] = None
    email: Optional[str] = None


class RegisterRequest(BaseModel):
    """Registration request"""
    email: str
    password: str
    display_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request"""
    email: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 Access Token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建 Refresh Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """解码 Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    token_data = decode_token(token)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/register", response_model=Token)
@limiter.limit("3/minute")
async def register(request: Request, reg_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account

    - **email**: Valid email address
    - **password**: Minimum 6 characters
    - **display_name**: Optional display name
    """
    from app.utils.security import hash_password
    import uuid

    import re
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', reg_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    # Validate password length
    if len(reg_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )

    # Check if email already exists
    existing = db.query(User).filter(User.email == reg_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=reg_data.email,
        password_hash=hash_password(reg_data.password),
        display_name=reg_data.display_name or reg_data.email.split('@')[0],
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens (auto-login after registration)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录

    - **email**: 用户邮箱
    - **password**: 用户密码
    """
    # 查找用户
    user = db.query(User).filter(
        (User.email == login_data.email) | (User.phone == login_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    
    # 生成 Token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """刷新 Token"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 验证是 refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        # 生成新 Token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
        }
        
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
    )


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, email: str, db: Session = Depends(get_db)):
    """
    Request a password reset token.

    In production, this would send an email. For MVP, the token is returned directly.
    """
    user = db.query(User).filter(User.email == email).first()

    # Always return success to avoid email enumeration
    if not user:
        return {"message": "If an account with this email exists, a reset link has been sent."}

    # Generate a short-lived reset token (15 minutes)
    reset_token = jwt.encode(
        {"sub": str(user.id), "email": user.email, "type": "reset", "exp": datetime.utcnow() + timedelta(minutes=15)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    # In production: send email with reset link
    # For MVP: return the token directly
    import logging
    logging.info(f"[PASSWORD RESET] Token for {email}: {reset_token}")

    return {
        "message": "If an account with this email exists, a reset link has been sent.",
        "reset_token": reset_token,  # MVP only — remove in production
    }


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Reset password using a reset token from forgot-password.
    """
    from app.utils.security import hash_password

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password_hash = hash_password(new_password)
        db.commit()

        return {"message": "Password has been reset successfully. You can now log in with your new password."}

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")


@router.post("/logout")
async def logout():
    """
    Logout user.

    Frontend should clear stored tokens.
    """
    return {"message": "Logged out successfully"}
