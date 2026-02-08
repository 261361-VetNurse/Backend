"""
Authentication Dependency (SQL Version)
FastAPI dependency for validating JWT tokens and getting current user
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database_sql import get_session
from app.services.auth_service_sql import get_user_by_id

security = HTTPBearer()


async def get_current_user_sql(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Get current user from JWT token (SQL version)
    
    Args:
        credentials: HTTP Bearer token
        session: Database session
        
    Returns:
        User dict with user_id and other user info
        
    Raises:
        HTTPException: 401 if token invalid/expired, 404 if user not found
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )

        # Convert to integer
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid User ID format in token"
            )

        # Get user from database
        user = await get_user_by_id(session, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        
        # Convert SQLAlchemy model to dict for backward compatibility
        return {
            "_id": user.user_id,  # For backward compatibility
            "user_id": user.user_id,
            "line_id": user.line_id,
            "display_name": user.display_name,
            "picture_url": user.picture_url,
            "fname": user.fname,
            "lname": user.lname,
            "email": user.email,
            "phone": user.phone,
            "is_registered": user.is_registered,
            "is_deleted": user.is_deleted,
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

get_current_user = get_current_user_sql
