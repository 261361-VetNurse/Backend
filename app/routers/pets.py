from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.register_schema import PetRegister 
from app.services.user_service_sql import (
    get_pets_by_owner, register_new_pet, get_pet_by_id, 
    update_pet_info, delete_pet, get_dashboard_data, add_pet_record, get_pet_records
)
from app.services.auth_dependency_sql import get_current_user 
from app.schemas.pet_schema import AppointmentCreate, MedicalHistoryCreate, PetNoteCreate, PetUpdateSchema, MedicationCreate
from app.database_sql import get_session

router = APIRouter(tags=["Pets 🐾"])

# API สำหรับดึงรายการสัตว์เลี้ยงทั้งหมด (My Pets Page)
@router.get("", summary="Get My Pets", description="Get all pets owned by current user") 
async def get_my_pets(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/pets - Get All User's Pets**
    
    Get list of all pets owned by the current user.
    
    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "_id": 1,
                "name": "Lucky",
                "species": "Dog",
                "breed": "Golden Retriever",
                "age": 3.5,
                "weight": 25.5,
                "profile_image": "https://example.com/image.jpg"
            }
        ]
    }
    ```
    """
    pets = await get_pets_by_owner(session, current_user["user_id"])
    return pets

# API สำหรับลงทะเบียนสัตว์เลี้ยงใหม่ (Register Pet)
@router.post("", status_code=201, summary="Register New Pet", description="Register a new pet for current user")
async def register_new_pet_endpoint(
    data: PetRegister, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **POST /v1/pets - Register New Pet**
    
    Register a new pet and link it to the current user.
    
    **Request Body:**
    ```json
    {
        "name": "Lucky",
        "species": "Dog",
        "breed": "Golden Retriever",
        "gender": "Male",
        "birthday": "2022-08-15",
        "weight": 25.5,
        "microchip": "123456789"
    }
    ```
    
    **Response:**
    ```json
    {
        "message": "Pet registered successfully",
        "pet_id": 2
    }
    ```
    """
    pet_id = await register_new_pet(session, current_user["user_id"], data)
    return {"message": "Pet registered successfully", "pet_id": pet_id}

# API สำหรับหน้า Dashboard Home
@router.get("/dashboard/home")
async def get_home_dashboard(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get dashboard summary data"""
    return await get_dashboard_data(session, current_user["user_id"])

@router.get("/{pet_id}")
async def get_pet_detail(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
): 
    """Get pet details by ID"""
    pet = await get_pet_by_id(session, pet_id) 
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

@router.patch("/{pet_id}")
async def update_pet_endpoint(
    pet_id: int, 
    data: PetUpdateSchema, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update pet information"""
    success = await update_pet_info(session, pet_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found or no changes made")
    return {"message": "Pet info updated"}

@router.delete("/{pet_id}")
async def delete_pet_endpoint(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Soft delete a pet"""
    success = await delete_pet(session, pet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"message": "Pet deleted successfully"}

# NOTE: Appointments and Medications endpoints moved to separate routers
# See: /v1/appointments and /v1/medications routers

# บันทึกอาการสัตว์เลี้ยง: POST /v1/pets/{pet_id}/symptoms
@router.post("/{pet_id}/symptoms")
async def record_pet_symptom(
    pet_id: int, 
    data: PetNoteCreate, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Record pet symptom/note"""
    note_id = await add_pet_record(session, pet_id, data.note, data.images if hasattr(data, 'images') else None)
    return {"message": "Symptom recorded successfully", "note_id": note_id}

# API สำหรับดึงประวัติการรักษาทั้งหมด
@router.get("/{pet_id}/medical-history")
async def get_pet_medical_history_endpoint(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all medical history/records for a pet"""
    return await get_pet_records(session, pet_id)

@router.post("/{pet_id}/medical-history")
async def add_user_medical_history(
    pet_id: int, 
    data: MedicalHistoryCreate, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add medical history record"""
    history_id = await add_pet_record(session, pet_id, data.note, data.images if hasattr(data, 'images') else None)
    return {"message": "Medical history recorded", "history_id": history_id}