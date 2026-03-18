"""
Password security utility module
Uses bcrypt for password hashing and verification
"""

from passlib.context import CryptContext

# Configure password context (supports multiple algorithms for future upgrades)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password (automatically salted)

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if the password matches, otherwise False
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a hash needs to be regenerated (used during algorithm upgrades)

    Args:
        hashed_password: Hashed password

    Returns:
        True if rehashing is needed
    """
    return pwd_context.needs_rehash(hashed_password)
