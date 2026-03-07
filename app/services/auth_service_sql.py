"""
Authentication Service (SQL Version)
Handles user authentication, JWT tokens, and Line Login
"""
import jwt
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models_sql.user_model import User, JWTToken


def create_access_token(user_id: int) -> str:
    """
    Create JWT access token for user
    
    Args:
        user_id: User ID (integer)
    
    Returns:
        JWT token string
    """
    now = int(time.time())
    payload = {
        "sub": str(user_id),  # Convert to string for JWT standard
        "iat": now,
        "exp": now + settings.JWT_EXPIRE_SECONDS,
        "type": "access"   
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return token


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get user by user_id
    
    Args:
        session: Database session
        user_id: User ID (integer)
    
    Returns:
        User object or None
    """
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_line_id(session: AsyncSession, line_id: str) -> Optional[User]:
    """
    Get user by line_id
    
    Args:
        session: Database session
        line_id: Line user ID
    
    Returns:
        User object or None
    """
    result = await session.execute(
        select(User).where(User.line_id == line_id)
    )
    return result.scalar_one_or_none()


async def upsert_user_from_line(session: AsyncSession, profile: dict) -> Tuple[User, bool]:
    """
    Insert or update user from Line profile
    
    Args:
        session: Database session
        profile: Line profile dict with userId, displayName, pictureUrl
    
    Returns:
        Tuple of (User object, is_new: bool)
    """
    line_id = profile["userId"]
    
    # Check if user exists
    existing = await get_user_by_line_id(session, line_id)
    
    if existing:
        # Update existing user
        existing.display_name = profile.get("displayName")
        existing.picture_url = profile.get("pictureUrl")
        # updated_at will be auto-updated by SQLAlchemy
        await session.commit()
        await session.refresh(existing)
        return existing, False
    
    # Create new user
    new_user = User(
        line_id=line_id,
        display_name=profile.get("displayName"),
        picture_url=profile.get("pictureUrl"),
        fname=profile.get("displayName", "").split()[0] if profile.get("displayName") else "User",
        lname=profile.get("displayName", "").split()[-1] if profile.get("displayName") and len(profile.get("displayName", "").split()) > 1 else "",
        is_registered=False,
        is_deleted=False,
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return new_user, True


async def save_jwt_token(
    session: AsyncSession, 
    user_id: int, 
    access_token: str, 
    key_id: Optional[str] = None
) -> JWTToken:
    """
    Save or update JWT token for user (1:1 relationship)
    
    Args:
        session: Database session
        user_id: User ID
        access_token: JWT token string
        key_id: Optional key ID from Line
    
    Returns:
        JWTToken object
    """
    # Calculate expiration time
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=settings.JWT_EXPIRE_SECONDS)
    
    # Check if token exists
    result = await session.execute(
        select(JWTToken).where(JWTToken.user_id == user_id)
    )
    existing_token = result.scalar_one_or_none()
    
    if existing_token:
        # Update existing token
        existing_token.access_token = access_token
        existing_token.key_id = key_id
        existing_token.expires_at = expires_at
    else:
        # Create new token
        existing_token = JWTToken(
            user_id=user_id,
            access_token=access_token,
            key_id=key_id,
            expires_at=expires_at,
        )
        session.add(existing_token)
    
    await session.commit()
    await session.refresh(existing_token)
    return existing_token


async def get_jwt_token(session: AsyncSession, user_id: int) -> Optional[JWTToken]:
    """
    Get JWT token by user_id
    
    Args:
        session: Database session
        user_id: User ID
    
    Returns:
        JWTToken object or None
    """
    result = await session.execute(
        select(JWTToken).where(JWTToken.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete_jwt_token(session: AsyncSession, user_id: int) -> bool:
    """
    Delete JWT token for user (logout)
    
    Args:
        session: Database session
        user_id: User ID
    
    Returns:
        True if deleted, False if not found
    """
    result = await session.execute(
        select(JWTToken).where(JWTToken.user_id == user_id)
    )
    token = result.scalar_one_or_none()
    
    if token:
        await session.delete(token)
        await session.commit()
        return True
    
    return False
