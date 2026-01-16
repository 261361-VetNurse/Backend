"""
Pet Owners Home Page Router - Dashboard
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
from bson import ObjectId
from datetime import datetime, timedelta
from app.database import get_database


router = APIRouter(
    prefix="/v1/dashboard/home",
    tags=["Dashboard - Home"]
)


def get_db():
    """Dependency to get database instance"""
    return get_database()


@router.get("")
async def get_home_page_dashboard(
    access_token: str = Header(..., alias="access_token", description="JWT access token"),
    db = Depends(get_db)
):
    """
    GET: Dashboard data for pet owner home page
    
    Requires access_token in header
    
    Returns:
    - fname: User's first name
    - lname: User's last name
    - pets: List of all user's pets with pet_id and profile_image
    - medicines_notifications: Today's medicine notifications with pet and medicine details
    - appointments: Current/future appointments with pet details
    """
    try:
        # 1. Validate JWT token and get user_id
        jwt_record = await db.JWT.find_one({"access_token": access_token})
        if not jwt_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        # Check if token is expired
        if jwt_record.get("expires_in") and jwt_record["expires_in"] < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired"
            )
        
        user_id_str = jwt_record["user_id"]
        user_id = ObjectId(user_id_str)
        
        # 2. Get user information
        user = await db.USERS.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 3. Get all pets of the user
        pets = await db.PETS.find({"user_id": user_id}).to_list(length=100)
        pets_data = [
            {
                "pet_id": str(pet["_id"]),
                "profile_image": pet.get("profile_image", "")
            }
            for pet in pets
        ]
        
        # 4. Get today's medicine notifications (only today)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        medicine_notifications = await db.MEDICINES_NOTIFICATION.find({
            "user_id": user_id,
            "notification_at": {
                "$gte": today_start,
                "$lt": today_end
            }
        }).to_list(length=100)
        
        # Populate medicine and pet details for notifications
        notifications_data = []
        for notif in medicine_notifications:
            # Get medicine details
            medicine = await db.MEDICINES.find_one({"_id": notif["medicine_id"]})
            medicine_name = medicine["name"] if medicine else "Unknown Medicine"
            
            # Get pet details
            pet = await db.PETS.find_one({"_id": notif["pet_id"]})
            pet_info = {
                "name": pet["name"] if pet else "Unknown Pet",
                "profile_image": pet.get("profile_image", "") if pet else ""
            }
            
            notifications_data.append({
                "_id": str(notif["_id"]),
                "title": notif["title"],
                "medicine_id": str(notif["medicine_id"]),
                "medicine_name": medicine_name,
                "pet_id": str(notif["pet_id"]),
                "pet_name": pet_info["name"],
                "pet_image": pet_info["profile_image"],
                "notification_at": notif["notification_at"],
                "status": notif.get("status", "pending"),
                "istaken": notif.get("istaken", False)
            })
        
        # 5. Get current/future appointments (not past)
        current_time = datetime.utcnow()
        
        appointments = await db.APPOINTMENTS.find({
            "user_id": user_id,
            "appointment_date": {"$gte": current_time}
        }).sort("appointment_date", 1).to_list(length=100)
        
        # Populate pet details and notification status for appointments
        appointments_data = []
        for appt in appointments:
            # Get pet details
            pet = await db.PETS.find_one({"_id": appt["_id"]})
            pet_info = {
                "name": pet["name"] if pet else "Unknown Pet",
                "profile_image": pet.get("profile_image", "") if pet else ""
            }
            
            # Get appointment notification details
            appt_notification = await db.APPOINTMENTS_NOTIFICATION.find_one({"appointment_id": appt["_id"]})
            notification_status = appt_notification.get("status", "pending") if appt_notification else "pending"
            
            appointments_data.append({
                "_id": str(appt["_id"]),
                "pet_id": str(appt["pet_id"]),
                "pet_name": pet_info["name"],
                "pet_image": pet_info["profile_image"],
                "appointment_date": appt["appointment_date"],
                "status": appt.get("status", "pending"),
                "notification_status": notification_status,
                "note": appt.get("note", "")
            })
        
        # 6. Return dashboard data
        return {
            "success": True,
            "data": {
                "fname": user["fname"],
                "lname": user.get("lname", ""),
                "pets": pets_data,
                # "line_profile": None,  # TODO: Implement LINE profile integration
                "medicines_notifications": notifications_data,
                "appointments": appointments_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )
