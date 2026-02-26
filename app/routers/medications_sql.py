"""
Medications Router (SQL Version)
API Endpoints for Medicine & Notification Management
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime, date as date_type
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, File, UploadFile
from app.services.ocr_service import scan_medication_label
from app.database_sql import get_session
from app.services.auth_dependency_sql import get_current_user
from app.services.medicine_service_sql import MedicineServiceSQL
from app.models_sql.medicine_model import Medicine, MedicineNotification
from app.models_sql.pet_model import Pet
from app.schemas.medicine import MedicineCreate, MedicineUpdate
from app.schemas.response_models import NotificationListResponse, SuccessResponse, GroupedMedicineNotification, ReminderSlot

router = APIRouter(tags=["Medications"])

# router = APIRouter(prefix="/v1/medications", tags=["Medications"])


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
    
    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "notification_id": 1,
                "title": "Time to give Amoxicillin to Lucky",
                "notification_at": "2026-02-08T08:00:00",
                "istaken": false,
                "pet_id": 1
            }
        ]
    }
    ```
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
    """
    **GET /v1/medications/{notification_id} - Get Notification Details**
    
    Get detailed information about a specific medicine notification including pet and medicine details.
    
    **Path Parameters:**
    - **notification_id**: Notification ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "notification_id": 1,
            "title": "Time to give Amoxicillin to Lucky",
            "notification_at": "2026-02-08T08:00:00",
            "istaken": true,
            "taken_at": "2026-02-08T22:07:04",
            "pet_id": 1,
            "pet_name": "Lucky",
            "pet_image": "https://example.com/lucky.jpg",
            "medicine_id": 1,
            "medicine_name": "Amoxicillin",
            "dosage": "2 tablets",
            "frequency": "-1",
            "reminder_time": ["08:00", "20:00"],
            "time_per_day": 2
        }
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


@router.get("/medicines/filter", summary="Filter Medicines by Pet", description="Get medicines filtered by pet_id with pet information")
async def filter_medicines_by_pet(
    pets_id: int = Query(..., description="Pet ID to filter medicines", example=1),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/medications/medicines/filter?pets_id={pet_id} - Filter Medicines by Pet**
    
    Get all medicines for a specific pet with pet information (name and image).
    
    **Query Parameters:**
    - **pets_id** (required): Pet ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "medicine_id": 1,
                "medicine_name": "Amoxicillin",
                "medicine_dosage": "1 tablet",
                "medicine_frequency": "-1",
                "pet_name": "Lucky",
                "pet_image": "https://example.com/lucky.jpg",
                "reminder_time": ["08:00", "20:00"]
            }
        ]
    }
    ```
    """
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


@router.post("/scan")
async def scan_label(file: UploadFile = File(...)):
    mime_type = file.content_type 
    
    if not mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="ไฟล์ต้องเป็นรูปภาพเท่านั้น")
        
    content = await file.read()
    
    result = await scan_medication_label(content, mime_type) 
    return {"status": "success", "data": result}