"""
密码安全工具模块
使用 bcrypt 进行密码哈希和验证
"""

from passlib.context import CryptContext

# 配置密码上下文（支持多种算法，方便未来升级）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    哈希密码（自动加盐）
    
    Args:
        password: 明文密码
        
    Returns:
        哈希后的密码字符串
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        True 如果密码匹配，否则 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    检查哈希是否需要重新生成（算法升级时使用）
    
    Args:
        hashed_password: 哈希后的密码
        
    Returns:
        True 如果需要重新哈希
    """
    return pwd_context.needs_rehash(hashed_password)
