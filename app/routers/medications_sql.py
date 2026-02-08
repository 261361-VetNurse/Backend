"""
Medications Router (SQL Version)
API Endpoints for Medicine & Notification Management
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime, date as date_type
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_sql import get_session
from app.services.auth_dependency_sql import get_current_user
from app.services.medicine_service_sql import MedicineServiceSQL
from app.models_sql.medicine_model import Medicine, MedicineNotification
from app.models_sql.pet_model import Pet
from app.schemas.medicine import MedicineCreate, MedicineUpdate
from app.schemas.response_models import (
    NotificationListResponse, NotificationDetailResponse, 
    MedicineListResponse, MedicineCreateResponse, SuccessResponse
)

router = APIRouter(tags=["Medications 💊"])


@router.get("", response_model=NotificationListResponse)
async def list_medications(
    pets_id: Optional[int] = Query(None, description="Filter by pet ID"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/medications - Medicine Notification Feed**
    
    Get list of medicine notifications for current user's pets.
    Can filter by specific pet and/or date.
    
    **Query Parameters:**
    - **pets_id** (optional): Filter notifications for specific pet
    - **date** (optional): Filter by date in YYYY-MM-DD format (default: today)
    
    **Returns:**
    - List of notifications with ID, title, time, taken status, and pet ID
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
            filter_date = datetime.utcnow().date()
        
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
        
        # Execute query
        result = await session.execute(
            select(MedicineNotification)
            .where(and_(*conditions))
            .order_by(MedicineNotification.notification_at.asc())
        )
        notifications = result.scalars().all()
        
        return {
            "success": True,
            "data": [
                {
                    "_id": notif.notification_id,
                    "notification_id": notif.notification_id,
                    "title": notif.title,
                    "notification_at": notif.notification_at.isoformat(),
                    "istaken": notif.istaken,
                    "pet_id": notif.pet_id,
                }
                for notif in notifications
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{notification_id}", response_model=NotificationDetailResponse)
async def get_notification_detail(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/medications/{notification_id} - Get Notification Details**
    
    Get detailed information about a specific medicine notification.
    
    **Path Parameters:**
    - **notification_id**: Notification ID (integer)
    
    **Returns:**
    - Detailed notification information including medicine, pet, and user IDs
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
    
    return {
        "success": True,
        "data": {
            "notification_id": notification.notification_id,
            "title": notification.title,
            "notification_at": notification.notification_at.isoformat(),
            "istaken": notification.istaken,
            "pet_id": notification.pet_id,
            "pet_name": pet.name if pet else None,
            "medicine_id": notification.medicine_id,
            "medicine_name": medicine.name if medicine else None,
            "dosage": medicine.dosage if medicine else None,
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
    """
    **GET /v1/medications/medicines/by-pet/{pet_id} - Get All Pet's Medicines**
    
    Get complete list of all medicines for a specific pet with full details.
    
    **Path Parameters:**
    - **pet_id**: Pet ID (integer)
    
    **Returns:**
    - List of all medicines with complete information including:
      - Basic info (name, dosage, frequency)
      - Schedule (start_date, end_date, reminder_time)
      - Status (active/stopped)
      - Additional info (notes, properties, images)
    
    **Response Example:**
    ```json
    {
        "success": true,
        "data": [
            {
                "medicine_id": 5,
                "name": "Amoxicillin",
                "dosage": "1 tablet",
                "frequency": "-1",
                "status": "TAKE",
                "start_date": "2026-02-01T00:00:00",
                "end_date": "2026-02-28T00:00:00",
                "reminder_time": ["08:00", "20:00"],
                "notes": ["เริ่มรับประทานวันที่ 1 ก.พ.", "กินหลังอาหาร"],
                "properties": "ยาปฏิชีวนะรักษาการติดเชื้อ",
                "image_urls": ["https://example.com/medicine1.jpg"],
                "created_at": "2026-02-01T10:00:00",
                "updated_at": "2026-02-01T10:00:00"
            }
        ]
    }
    ```
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
    
    # Get all medicines for this pet
    medicines = await MedicineServiceSQL.get_medicines_by_pet(session, pet_id)
    
    return {
        "success": True,
        "data": [
            {
                "medicine_id": med.medicine_id,
                "name": med.name,
                "dosage": med.dosage,
                "frequency": med.frequency,
                "status": med.status,
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


@router.post("/medicines", status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine_data: MedicineCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **POST /v1/medications/medicines - Create New Medicine**
    
    Create a new medicine schedule. Automatically generates notifications.
    
    **Request Body:**
    ```json
    {
        "pet_id": 2,
        "name": "Amoxicillin",
        "dosage": "1 tablet",
        "frequency": "-1",
        "reminder_time": ["08:00", "20:00"],
        "start_date": "2026-02-01T00:00:00",
        "end_date": "2026-02-28T00:00:00"
    }
    ```
    
    **Frequency values:**
    - `-1` = Daily
    - `0-6` = Specific weekdays (0=Monday, 6=Sunday)
    - `0,2,4` = Multiple days (Mon, Wed, Fri)
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Medicine created successfully",
        "medicine_id": 5
    }
    ```
    """
    result = await MedicineServiceSQL.create_medicine(
        session, 
        medicine_data.pet_id,
        medicine_data.dict()
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
    **PATCH /v1/medications/medicines/{medicine_id} - Update Medicine**
    
    Update medicine information. Handles status changes and note additions.
    
    **Path Parameters:**
    - **medicine_id**: Medicine ID (integer)
    
    **Request Body:** (all fields optional)
    ```json
    {
        "status": "STOP",
        "note": "Completed treatment"
    }
    ```
    
    **Status values:**
    - `TAKE` = Active (medicine is being taken)
    - `STOP` = Stopped (deletes future notifications)
    
    **Note:** Keeps only last 3 notes
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Medicine updated successfully"
    }
    ```
    """
    result = await MedicineServiceSQL.update_medicine(
        session,
        medicine_id,
        current_user["user_id"],
        medicine_data.dict(exclude_unset=True)
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
    """
    **DELETE /v1/medications/medicines/{medicine_id} - Delete Medicine**
    
    Soft delete a medicine and its associated notifications.
    
    **Path Parameters:**
    - **medicine_id**: Medicine ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Medicine deleted"
    }
    ```
    """
    success = await MedicineServiceSQL.delete_medicine(session, medicine_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    return {"success": True, "message": "Medicine deleted"}
