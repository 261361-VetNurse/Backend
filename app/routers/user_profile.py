"""
User Profile Router (SQL Version)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_sql import get_session
from app.services.auth_dependency_sql import get_current_user
from app.services.user_service_sql import get_user_profile, update_user_profile

router = APIRouter(
    prefix="/v1/user",
    tags=["User Profile 👤"]
)


@router.get("/profile")
async def get_user_profile_endpoint(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get current user's profile information"""
    try:
        profile = await get_user_profile(session, current_user["user_id"])
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "data": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )


@router.patch("/profile")
async def update_user_profile_endpoint(
    profile_data: dict,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update current user's profile information"""
    try:
        success = await update_user_profile(
            session,
            current_user["user_id"],
            profile_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or no changes made"
            )
        
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )
