"""
User Profile Router
"""

from fastapi import APIRouter, HTTPException, status, Header
from app.database import get_database
from datetime import datetime
from bson import ObjectId

router = APIRouter(
    prefix="/v1/user",
    tags=["User Profile"]
)


async def get_current_user_from_token(access_token: str, db):
    """Validate access token and return user_id"""
    jwt_record = await db.JWT.find_one({"access_token": access_token})
    
    if not jwt_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    if jwt_record.get("expires_in") and jwt_record["expires_in"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired"
        )
    
    return jwt_record["user_id"]


@router.get("/profile")
async def get_user_profile(
    access_token: str = Header(..., alias="access_token")
):
    """
    Get current user's profile information
    
    Returns:
    - User profile data including name, contact info, etc.
    """
    db = get_database()
    
    try:
        # Get user_id from token
        user_id_str = await get_current_user_from_token(access_token, db)
        user_id = ObjectId(user_id_str)
        
        # Get user from database
        user = await db.USERS.find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Extract contact info if it exists
        contact = user.get("contact", {})
        address = user.get("address", {})
        
        return {
            "success": True,
            "data": {
                "id": str(user["_id"]),
                "fname": user.get("fname", ""),
                "lname": user.get("lname", ""),
                "display_name": user.get("display_name", ""),
                "line_id": user.get("line_id", ""),
                "picture_url": user.get("picture_url", ""),
                "role": user.get("role", "pet_owner"),
                "contact": {
                    "phone": contact.get("phone", ""),
                    "email": contact.get("email", ""),
                    "gender": contact.get("gender", "")
                },
                "address": {
                    "street": address.get("street", ""),
                    "city": address.get("city", ""),
                    "province": address.get("province", ""),
                    "postal_code": address.get("postal_code", "")
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )


@router.patch("/profile")
async def update_user_profile(
    profile_data: dict,
    access_token: str = Header(..., alias="access_token")
):
    """
    Update current user's profile information
    
    Body:
    - fname, lname, contact, address, etc.
    """
    db = get_database()
    
    try:
        # Get user_id from token
        user_id_str = await get_current_user_from_token(access_token, db)
        user_id = ObjectId(user_id_str)
        
        # Update user
        update_data = {
            **profile_data,
            "updated_at": datetime.utcnow()
        }
        
        result = await db.USERS.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
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
