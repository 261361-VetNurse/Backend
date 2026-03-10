"""
Medications Router (SQL Version)
API Endpoints for Medicine & Notification Management
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_sql import get_session
from app.services.auth_dependency_sql import get_current_user
from app.services.medicine_service_sql import MedicineServiceSQL
from app.models_sql.medicine_model import Medicine, MedicineNotification
from app.models_sql.pet_model import Pet
from app.schemas.medicine import MedicineCreate, MedicineUpdate
from app.schemas.response_models import NotificationListResponse, SuccessResponse, GroupedMedicineNotification, ReminderSlot

router = APIRouter(tags=["Medications"])


@router.get("", response_model=NotificationListResponse)
async def list_medications(
    pets_id: Optional[int] = Query(None, description="Filter by pet ID"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get medicine notification feed for current user.
    Optionally filter by pet and/or date (defaults to today).
    """
    try:
        # Parse date
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            filter_date = datetime.now(timezone.utc).replace(tzinfo=None).date()
        
        # Build query
        conditions = [
            MedicineNotification.user_id == current_user["user_id"]
        ]
        
        if pets_id:
            conditions.append(MedicineNotification.pet_id == pets_id)
        
        # Filter by date (notification_at on same day)
        start_datetime = datetime.combine(filter_date, datetime.min.time())
        end_datetime = datetime.combine(filter_date, datetime.max.time())
        conditions.append(MedicineNotification.notification_at >= start_datetime)
        conditions.append(MedicineNotification.notification_at <= end_datetime)
        
        # Execute query with joins to get pet and medicine details
        result = await session.execute(
            select(MedicineNotification, Pet, Medicine)
            .join(Pet, MedicineNotification.pet_id == Pet.pet_id)
            .join(Medicine, MedicineNotification.medicine_id == Medicine.medicine_id)
            .where(and_(*conditions))
            .order_by(MedicineNotification.notification_at.asc())
        )
        rows = result.all()
        
        # Grouping Logic
        grouped_data = {}
        
        for notif, pet, medicine in rows:
            key = (notif.medicine_id, notif.pet_id)
            
            if key not in grouped_data:
                grouped_data[key] = {
                    "medicine_id": notif.medicine_id,
                    "pet_id": notif.pet_id,
                    "pet_name": pet.name if pet else "",
                    "pet_image": pet.profile_image if pet else None,
                    "medicine_name": medicine.name if medicine else "",
                    "dosage": medicine.dosage if medicine else None,
                    "frequency": medicine.frequency if medicine else None,
                    "reminder_time": medicine.reminder_time if medicine else [],
                    "start_date": medicine.start_date.isoformat() if medicine and medicine.start_date else None,
                    "end_date": medicine.end_date.isoformat() if medicine and medicine.end_date else None,
                    "status": medicine.status if medicine else None,
                    "is_deleted": medicine.is_deleted if medicine else False,
                    "reminders": []
                }
            
            # Determine status
            status_str = "pending"
            if notif.istaken:
                status_str = "taken"
            
            # Extract time from notification_at
            time_str = notif.notification_at.strftime("%H:%M")
            
            # Get taken_at timestamp (updated_at when istaken=true)
            taken_at_str = notif.updated_at.isoformat() if notif.istaken and notif.updated_at else None

            grouped_data[key]["reminders"].append(
                ReminderSlot(
                    notification_id=notif.notification_id,
                    time=time_str,
                    status=status_str,
                    taken_at=taken_at_str
                )
            )
            
        # Convert to list
        response_data = [GroupedMedicineNotification(**data) for data in grouped_data.values()]
        
        return {
            "success": True,
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{notification_id}")
async def get_notification_detail(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get full details of a medicine notification including pet and medicine info."""
    result = await session.execute(
        select(MedicineNotification)
        .where(and_(
            MedicineNotification.notification_id == notification_id,
            MedicineNotification.user_id == current_user["user_id"]
        ))
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Get medicine details
    medicine_result = await session.execute(
        select(Medicine).where(Medicine.medicine_id == notification.medicine_id)
    )
    medicine = medicine_result.scalar_one_or_none()
    
    # Get pet details
    pet_result = await session.execute(
        select(Pet).where(Pet.pet_id == notification.pet_id)
    )
    pet = pet_result.scalar_one_or_none()
    
    # Calculate time_per_day from reminder_time array length
    time_per_day = len(medicine.reminder_time) if medicine and medicine.reminder_time else 0
    
    # Get taken_at timestamp (updated_at when istaken=true)
    taken_at = notification.updated_at if notification.istaken else None
    
    return {
        "success": True,
        "data": {
            "notification_id": notification.notification_id,
            "title": notification.title,
            "notification_at": notification.notification_at.isoformat(),
            "istaken": notification.istaken,
            "taken_at": taken_at.isoformat() if taken_at else None,
            "pet_id": notification.pet_id,
            "pet_name": pet.name if pet else None,
            "pet_image": pet.profile_image if pet else "",
            "medicine_id": notification.medicine_id,
            "medicine_name": medicine.name if medicine else None,
            "dosage": medicine.dosage if medicine else None,
            "frequency": medicine.frequency if medicine else None,
            "status": medicine.status if medicine else None,
            "start_date": medicine.start_date.isoformat() if medicine and medicine.start_date else None,
            "end_date": medicine.end_date.isoformat() if medicine and medicine.end_date else None,
            "notes": medicine.notes if medicine and medicine.notes else [],
            "reminder_time": medicine.reminder_time if medicine else [],
            "time_per_day": time_per_day
        }
    }


@router.patch("/{notification_id}/taken")
async def mark_notification_taken(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **PATCH /v1/medications/{notification_id}/taken - Mark Medicine as Taken**
    
    Mark a medicine notification as taken.
    
    **Path Parameters:**
    - **notification_id**: Notification ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Marked as taken"
    }
    ```
    """
    result = await session.execute(
        select(MedicineNotification)
        .where(and_(
            MedicineNotification.notification_id == notification_id,
            MedicineNotification.user_id == current_user["user_id"]
        ))
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.istaken = True
    await session.commit()
    
    return {"success": True, "message": "Marked as taken"}


@router.get("/medicines/by-pet/{pet_id}", summary="Get All Medicines", description="Get all medicines for a specific pet with full details")
async def get_medicines_by_pet(
    pet_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get complete medicine list for a specific pet including schedule and status.
    Returns ALL medicines including soft-deleted ones so the frontend can display them as inactive.
    """
    # Verify pet belongs to user
    pet_result = await session.execute(
        select(Pet).where(and_(
            Pet.pet_id == pet_id,
            Pet.user_id == current_user["user_id"]
        ))
    )
    pet = pet_result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Get ALL medicines for this pet, including soft-deleted ones
    # (Frontend handles is_deleted display logic)
    med_result = await session.execute(
        select(Medicine)
        .where(Medicine.pet_id == pet_id)
        .order_by(Medicine.created_at.desc())
    )
    medicines = med_result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "medicine_id": med.medicine_id,
                "pet_id": med.pet_id,
                "name": med.name,
                "dosage": med.dosage,
                "frequency": med.frequency,
                "status": med.status,
                "is_deleted": med.is_deleted,
                "start_date": med.start_date.isoformat() if med.start_date else None,
                "end_date": med.end_date.isoformat() if med.end_date else None,
                "reminder_time": med.reminder_time if med.reminder_time else [],
                "notes": med.notes if med.notes else [],
                "properties": med.properties,
                "image_urls": med.image_urls if med.image_urls else [],
                "created_at": med.created_at.isoformat() if med.created_at else None,
                "updated_at": med.updated_at.isoformat() if med.updated_at else None
            }
            for med in medicines
        ]
    }


@router.get("/medicines/filter", summary="Filter Medicines by Pet", description="Get medicines filtered by pet_id with pet information")
async def filter_medicines_by_pet(
    pets_id: int = Query(..., description="Pet ID to filter medicines", example=1),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get medicines for a specific pet (by query param) with pet name and image."""
    # Verify pet ownership
    pet_result = await session.execute(
        select(Pet).where(and_(
            Pet.pet_id == pets_id,
            Pet.user_id == current_user["user_id"],
            Pet.is_deleted == False
        ))
    )
    pet = pet_result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found or access denied"
        )
    
    # Get medicines for this pet
    medicines = await MedicineServiceSQL.get_medicines_by_pet(session, pets_id)
    
    return {
        "success": True,
        "data": [
            {
                "medicine_id": med.medicine_id,
                "medicine_name": med.name,
                "medicine_dosage": med.dosage if med.dosage else "",
                "medicine_frequency": med.frequency,
                "pet_name": pet.name,
                "pet_image": pet.profile_image if pet.profile_image else "",
                "reminder_time": med.reminder_time if med.reminder_time else []
            }
            for med in medicines
        ]
    }


@router.post("/medicines", status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine_data: MedicineCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new medicine schedule. Auto-generates notifications.
    Frequency: -1=daily, 0-6=specific weekday, comma-separated for multiple days.
    """
    pet_check = await session.execute(
        select(Pet).where(and_(
            Pet.pet_id == medicine_data.pet_id,
            Pet.user_id == current_user["user_id"],
            Pet.is_deleted == False
        ))
    )
    if not pet_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Pet not found")

    result = await MedicineServiceSQL.create_medicine(
        session, 
        medicine_data.pet_id,
        medicine_data.model_dump()
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.patch("/medicines/{medicine_id}")
async def update_medicine(
    medicine_id: int,
    medicine_data: MedicineUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Update medicine info or status.
    status=STOP deletes future notifications and appends a note.
    Schedule changes regenerate notifications.
    """
    result = await MedicineServiceSQL.update_medicine(
        session,
        medicine_id,
        current_user["user_id"],
        medicine_data.model_dump(exclude_unset=True)
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.delete("/medicines/{medicine_id}")
async def delete_medicine(
    medicine_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Soft-delete a medicine and its associated notifications."""
    success = await MedicineServiceSQL.delete_medicine(session, medicine_id, current_user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    return {"success": True, "message": "Medicine deleted"}
