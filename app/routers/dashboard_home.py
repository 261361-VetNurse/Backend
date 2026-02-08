"""
Pet Owners Home Page Router - Dashboard
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models_sql.base import get_async_session
from app.models_sql import User, Pet, Medicine, MedicineNotification, Appointment, AppointmentNotification, JWTToken


router = APIRouter(
    prefix="/v1/dashboard/home",
    tags=["Dashboard 🏠"]
)


@router.get("")
async def get_home_page_dashboard(
    access_token: str = Header(..., alias="access_token", description="JWT access token"),
    session: AsyncSession = Depends(get_async_session)
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
        result = await session.execute(
            select(JWTToken).where(JWTToken.access_token == access_token)
        )
        jwt_record = result.scalar_one_or_none()
        
        if not jwt_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        # Check if token is expired
        if jwt_record.expires_in and jwt_record.expires_in < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired"
            )
        
        user_id = jwt_record.user_id
        
        # 2. Get user information
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 3. Get all pets of the user
        result = await session.execute(
            select(Pet).where(Pet.user_id == user_id)
        )
        pets = result.scalars().all()
        
        pets_data = [
            {
                "pet_id": str(pet.id),
                "name": pet.name,
                "profile_image": pet.profile_image or ""
            }
            for pet in pets
        ]
        
        # 4. Get today's medicine notifications (only today)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get medicine notifications with medicine and pet details
        result = await session.execute(
            select(MedicineNotification)
            .options(
                selectinload(MedicineNotification.medicine),
                selectinload(MedicineNotification.pet)
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
            notifications_data.append({
                "_id": str(notif.id),
                "title": notif.title,
                "medicine_id": str(notif.medicine_id),
                "medicine_name": notif.medicine.name if notif.medicine else "Unknown Medicine",
                "pet_id": str(notif.pet_id),
                "pet_name": notif.pet.name if notif.pet else "Unknown Pet",
                "pet_image": notif.pet.profile_image if notif.pet else "",
                "notification_at": notif.notification_at,
                "status": notif.status or "pending",
                "istaken": notif.istaken or False
            })
        
        # 5. Get current/future appointments (not past)
        current_time = datetime.utcnow()
        
        result = await session.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.pet),
                selectinload(Appointment.notification)
            )
            .where(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.appointment_date >= current_time
                )
            )
            .order_by(Appointment.appointment_date)
        )
        appointments = result.scalars().all()
        
        # Build appointments data
        appointments_data = []
        for appt in appointments:
            notification_status = appt.notification.status if appt.notification else "pending"
            
            appointments_data.append({
                "_id": str(appt.id),
                "pet_id": str(appt.pet_id),
                "pet_name": appt.pet.name if appt.pet else "Unknown Pet",
                "pet_image": appt.pet.profile_image if appt.pet else "",
                "appointment_date": appt.appointment_date,
                "status": appt.status or "pending",
                "notification_status": notification_status,
                "note": appt.note or ""
            })
        
        # 6. Return dashboard data
        return {
            "success": True,
            "data": {
                "fname": user.fname,
                "lname": user.lname or "",
                "pets": pets_data,
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

