"""
Notifications Router (SQL Version)
API Endpoints for Unified Notification Feed
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database_sql import get_session
from app.services.auth_dependency_sql import get_current_user
from app.models_sql.medicine_model import MedicineNotification, Medicine
from app.models_sql.appointment_model import AppointmentNotification, Appointment
from app.models_sql.pet_model import Pet

router = APIRouter(tags=["Notifications"])


@router.get("", summary="Get All Notifications")
async def get_all_notifications(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/notifications - Unified Notification Feed**
    
    Get all notifications (Medicine + Appointment) for the current user, sorted by date (newest first).
    
    **Query Parameters:**
    - **limit** (optional): Max number of notifications to return (default: 50)
    
    **Response:**
    Returns a unified list of notifications.
    """
    try:
        user_id = current_user["user_id"]
        
        # 1. Fetch Medicine Notifications
        # Join with Medicine and Pet to get details
        med_query = (
            select(MedicineNotification)
            .options(
                selectinload(MedicineNotification.medicine).selectinload(Medicine.pet)
            )
            .where(and_(
                MedicineNotification.user_id == user_id,
                MedicineNotification.status == "sent"
            ))
            .order_by(desc(MedicineNotification.notification_at))
            .limit(limit)
        )
        med_result = await session.execute(med_query)
        med_notifs = med_result.scalars().all()
        
        # 2. Fetch Appointment Notifications
         # Join with Appointment and Pet
        appt_query = (
            select(AppointmentNotification)
            .options(
                selectinload(AppointmentNotification.appointment).selectinload(Appointment.pet)
            )
            .where(and_(
                AppointmentNotification.user_id == user_id,
                AppointmentNotification.status == "sent"
            ))
            .order_by(desc(AppointmentNotification.notification_at))
            .limit(limit)
        )
        appt_result = await session.execute(appt_query)
        appt_notifs = appt_result.scalars().all()
        
        # 3. Combine and Sort
        combined = []
        
        # Process Medicine Notifications
        for n in med_notifs:
            # Get pet info through medicine relationship
            pet = n.medicine.pet if n.medicine else None
            
            combined.append({
                "type": "medicine",
                "notification_id": n.notification_id,
                "title": n.title,
                "notification_at": n.notification_at,
                "is_read": n.status != 'pending',
                "status": n.status,
                "payload": {
                    "medicine_id": n.medicine_id,
                    "medicine_name": n.medicine.name if n.medicine else "Unknown Medicine",
                    "pet_id": n.pet_id,
                    "pet_name": pet.name if pet else "Unknown Pet",
                    "pet_image": pet.profile_image if pet else None,
                    "dosage": n.medicine.dosage if n.medicine else None,
                    "istaken": n.istaken
                },
                "created_at": n.created_at
            })
            
        # Process Appointment Notifications
        for n in appt_notifs:
            # Get pet info through appointment relationship
            pet = n.appointment.pet if n.appointment else None

            combined.append({
                "type": "appointment",
                "notification_id": n.notification_id,
                "title": n.title,
                "notification_at": n.notification_at,
                "is_read": n.status != 'pending', # rough approximation
                "status": n.status,
                "payload": {
                    "appointment_id": n.appointment_id,
                    "location": n.appointment.location if n.appointment else "Unknown Location",
                    "pet_id": n.pet_id,
                    "pet_name": pet.name if pet else "Unknown Pet",
                    "pet_image": pet.profile_image if pet else None,
                    "appointment_date": n.appointment.appointment_date if n.appointment else None
                },
                "created_at": n.created_at
            })
            
        # Sort by notification_at descending
        combined.sort(key=lambda x: x["notification_at"], reverse=True)
        
        # Apply limit after combining
        final_list = combined[:limit]
        
        return {
            "success": True,
            "data": final_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )
