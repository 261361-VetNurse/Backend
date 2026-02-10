"""
Pet Owners Home Page Router - Dashboard
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models_sql.base import get_async_session
from app.models_sql import Pet, Medicine, MedicineNotification, Appointment
from app.services.auth_dependency_sql import get_current_user


router = APIRouter(
    prefix="/v1/dashboard/home",
    tags=["Dashboard"]
)


@router.get("", summary="Get Dashboard Data", description="Get dashboard data for pet owner home page")
async def get_home_page_dashboard(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    **GET /v1/dashboard/home - Dashboard Data**
    
    Get dashboard data for pet owner home page.
    Requires Bearer token in Authorization header.
    
    **Returns:**
    - **fname**: User's first name
    - **lname**: User's last name
    - **profile_image**: User's profile image URL
    - **pets**: List of active pets with pet_id, name, profile_image, in_medical
    - **medicines_notifications**: Today's medicine notifications with medicine and pet details
    - **appointments**: Current/future appointments (excluding soft-deleted)
    """
    try:
        user_id = current_user["user_id"]
        
        # 1. Get all pets of the user (exclude soft-deleted)
        result = await session.execute(
            select(Pet).where(
                and_(Pet.user_id == user_id, Pet.is_deleted == False)
            )
        )
        pets = result.scalars().all()
        
        pets_data = [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "profile_image": pet.profile_image or "",
                "in_medical": pet.in_medical
            }
            for pet in pets
        ]
        
        # 2. Get today's medicine notifications (only today)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get medicine notifications with medicine and pet details
        result = await session.execute(
            select(MedicineNotification)
            .options(
                selectinload(MedicineNotification.medicine).selectinload(Medicine.pet)
            )
            .where(
                and_(
                    MedicineNotification.user_id == user_id,
                    MedicineNotification.notification_at >= today_start,
                    MedicineNotification.notification_at < today_end
                )
            )
        )
        medicine_notifications = result.scalars().all()
        
        # Build notifications data
        notifications_data = []
        for notif in medicine_notifications:
            # Extract time from notification_at
            notification_time = notif.notification_at.strftime("%H:%M") if notif.notification_at else ""
            # Get pet info through medicine relationship
            pet = notif.medicine.pet if notif.medicine else None
            
            notifications_data.append({
                "_id": str(notif.notification_id),
                "notification_id": notif.notification_id,
                "title": notif.title,
                "medicine_id": str(notif.medicine_id),
                "medicine_name": notif.medicine.name if notif.medicine else "Unknown Medicine",
                "dosage": notif.medicine.dosage if notif.medicine else "",
                "frequency": notif.medicine.frequency if notif.medicine else "",
                "reminder_time": notif.medicine.reminder_time if notif.medicine else [],
                "pet_id": str(notif.pet_id),
                "pet_name": pet.name if pet else "Unknown Pet",
                "pet_image": pet.profile_image if pet else "",
                "notification_at": notif.notification_at,
                "time": notification_time,
                "status": notif.status or "pending",
                "istaken": notif.istaken or False
            })
        
        # 3. Get current/future appointments (not past)
        current_time = datetime.utcnow()
        
        result = await session.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.pet),
                selectinload(Appointment.notifications)
            )
            .where(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.appointment_date >= current_time,
                    Appointment.is_deleted == False
                )
            )
            .order_by(Appointment.appointment_date)
        )
        appointments = result.scalars().all()
        
        # Build appointments data
        appointments_data = []
        for appt in appointments:
            notification_status = appt.notifications[0].status if appt.notifications else "pending"
            
            appointments_data.append({
                "_id": str(appt.appointment_id),
                "appointment_id": appt.appointment_id,
                "pet_id": str(appt.pet_id),
                "pet_name": appt.pet.name if appt.pet else "Unknown Pet",
                "pet_image": appt.pet.profile_image if appt.pet else "",
                "location": appt.location or "",
                "appointment_date": appt.appointment_date,
                "status": appt.status or "pending",
                "notification_status": notification_status,
                "note": appt.note or ""
            })
        
        # 4. Return dashboard data
        return {
            "success": True,
            "data": {
                "fname": current_user.get("fname", "Pet Owner"),
                "lname": current_user.get("lname", ""),
                "profile_image": current_user.get("picture_url", ""),
                "pets": pets_data,
                "medicines_notifications": notifications_data,
                "appointments": appointments_data
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )


