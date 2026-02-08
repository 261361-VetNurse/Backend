"""
Pet Records Router (Symptom Records)
API Endpoints for Pet Health and Behavior Records
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_sql import get_session
from app.services.auth_dependency_sql import get_current_user
from app.services.pet_record_service_sql import PetRecordServiceSQL
from app.schemas.pet_record_schema import PetRecordCreate, PetRecordUpdate

router = APIRouter(
    prefix="/v1/symptom-records",
    tags=["Symptom Records"]
)


@router.get("/calendar", summary="Get Pet Records Calendar", description="Get all pet records for calendar view")
async def get_records_calendar(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/symptom-records/calendar - Get Pet Records Calendar**
    
    Get all pet health and behavior records for the current user's pets.
    Returns records sorted by most recent first.
    
    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "record_id": 1,
                "pet_id": 1,
                "pet_name": "ลัคกี้",
                "pet_image": "https://example.com/lucky.jpg",
                "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร",
                "note_image": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ],
                "time_added": "2026-02-08T14:30:00"
            }
        ]
    }
    ```
    """
    try:
        records = await PetRecordServiceSQL.get_records_by_user(
            session,
            current_user["user_id"]
        )
        
        return {
            "success": True,
            "data": records
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching records: {str(e)}"
        )


@router.get("/{record_id}", summary="Get Record Detail", description="Get detailed information about a specific pet record")
async def get_record_detail(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/symptom-records/{record_id} - Get Record Details**
    
    Get detailed information about a specific pet health/behavior record.
    
    **Path Parameters:**
    - **record_id**: Record ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "record_id": 1,
            "pet_id": 1,
            "pet_name": "ลัคกี้",
            "pet_image": "https://example.com/lucky.jpg",
            "date_added": "2026-02-08",
            "time_added": "14:30",
            "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร และดื่มน้ำน้อยกว่าปกติ",
            "note_image": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ]
        }
    }
    ```
    """
    record = await PetRecordServiceSQL.get_record_by_id(
        session,
        record_id,
        current_user["user_id"]
    )
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found or access denied"
        )
    
    return {
        "success": True,
        "data": record
    }


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create Pet Record", description="Create a new pet health/behavior record")
async def create_record(
    record_data: PetRecordCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **POST /v1/symptom-records - Create New Record**
    
    Create a new pet health or behavior record with optional images (max 4).
    
    **Request Body:**
    ```json
    {
        "pet_id": 1,
        "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร และดื่มน้ำน้อยกว่าปกติ",
        "note_image": [
            "https://cloudflare.example.com/pet-records/image1.jpg",
            "https://cloudflare.example.com/pet-records/image2.jpg"
        ]
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Record created successfully",
        "record_id": 1
    }
    ```
    """
    # Verify pet ownership
    from sqlalchemy import select, and_
    from app.models_sql.pet_model import Pet
    
    result = await session.execute(
        select(Pet).where(and_(
            Pet.pet_id == record_data.pet_id,
            Pet.user_id == current_user["user_id"],
            Pet.is_deleted == False
        ))
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found or access denied"
        )
    
    result = await PetRecordServiceSQL.create_record(
        session,
        record_data.pet_id,
        record_data.note,
        record_data.note_image
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error")
        )
    
    return {
        "success": True,
        "message": "Record created successfully",
        "record_id": result["record_id"]
    }


@router.patch("/{record_id}", summary="Update Pet Record", description="Update an existing pet record")
async def update_record(
    record_id: int,
    record_data: PetRecordUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **PATCH /v1/symptom-records/{record_id} - Update Record**
    
    Update an existing pet health/behavior record.
    
    **Path Parameters:**
    - **record_id**: Record ID (integer)
    
    **Request Body:** (all fields optional)
    ```json
    {
        "note": "อาการดีขึ้นมากหลังจากให้ยาและดูแลเป็นพิเศษ 2 วัน",
        "note_image": [
            "https://cloudflare.example.com/pet-records/updated1.jpg"
        ]
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Record updated successfully"
    }
    ```
    """
    result = await PetRecordServiceSQL.update_record(
        session,
        record_id,
        current_user["user_id"],
        record_data.model_dump(exclude_unset=True)
    )
    
    if not result["success"]:
        if "not found" in result.get("error", "").lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("error")
            )
    
    return result


@router.delete("/{record_id}", summary="Delete Pet Record", description="Delete a pet record permanently")
async def delete_record(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **DELETE /v1/symptom-records/{record_id} - Delete Record**
    
    Permanently delete a pet health/behavior record.
    
    **Path Parameters:**
    - **record_id**: Record ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Record deleted successfully"
    }
    ```
    """
    result = await PetRecordServiceSQL.delete_record(
        session,
        record_id,
        current_user["user_id"]
    )
    
    if not result["success"]:
        if "not found" in result.get("error", "").lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("error")
            )
    
    return result
