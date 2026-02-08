from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.register_schema import PetRegister 
from app.services.user_service_sql import (
    get_pets_by_owner, register_new_pet, get_pet_by_id, 
    update_pet_info, delete_pet, get_dashboard_data, add_pet_record, get_pet_records
)
from app.services.auth_dependency_sql import get_current_user 
from app.schemas.pet_schema import MedicalHistoryCreate, PetNoteCreate, PetUpdateSchema
from app.database_sql import get_session

router = APIRouter(tags=["Pets"])


@router.get("", summary="Get My Pets", description="Get all pets owned by current user") 
async def get_my_pets(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/pets - Get All User's Pets**
    
    Get list of all active (non-deleted) pets owned by the current user.
    
    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "pet_id": 1,
                "name": "Lucky",
                "species": "Dog",
                "breed": "Golden Retriever",
                "color": "Golden",
                "gender": "Male",
                "birth_date": "2022-03-15",
                "weight_kg": 25.5,
                "profile_image": "https://example.com/lucky.jpg",
                "in_medical": true,
                "infecund": false
            }
        ]
    }
    ```
    """
    pets = await get_pets_by_owner(session, current_user["user_id"])
    return pets

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
        "name": "ลัคกี้",
        "species": "Dog",
        "breed": "Golden Retriever",
        "gender": "Male",
        "birth_date": "2022-03-15",
        "color": "Golden",
        "weight_kg": 25.5,
        "infecund": false,
        "in_medical": false,
        "profile_image": "https://example.com/pets/lucky.jpg"
    }
    ```
    
    **Response (201):**
    ```json
    {
        "message": "Pet registered successfully",
        "pet_id": 2
    }
    ```
    """
    pet_id = await register_new_pet(session, current_user["user_id"], data)
    return {"message": "Pet registered successfully", "pet_id": pet_id}

@router.get("/dashboard/home")
async def get_home_dashboard(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get dashboard summary data"""
    return await get_dashboard_data(session, current_user["user_id"])

@router.get("/{pet_id}", summary="Get Pet Detail", description="Get detailed pet information by ID")
async def get_pet_detail(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
): 
    """
    **GET /v1/pets/{pet_id} - Get Pet Details**
    
    Get detailed information about a specific pet.
    Returns 404 if pet not found or soft-deleted.
    
    **Path Parameters:**
    - **pet_id**: Pet ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "pet_id": 1,
            "name": "Lucky",
            "species": "Dog",
            "breed": "Golden Retriever",
            "color": "Golden",
            "gender": "Male",
            "birth_date": "2022-03-15",
            "weight_kg": 25.5,
            "profile_image": "https://example.com/lucky.jpg",
            "in_medical": true,
            "infecund": false
        }
    }
    ```
    """
    pet = await get_pet_by_id(session, pet_id) 
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

@router.patch("/{pet_id}", summary="Update Pet Info", description="Update pet information (partial update)")
async def update_pet_endpoint(
    pet_id: int, 
    data: PetUpdateSchema, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **PATCH /v1/pets/{pet_id} - Update Pet Information**
    
    Update pet information. All fields are optional (partial update).
    
    **Path Parameters:**
    - **pet_id**: Pet ID (integer)
    
    **Request Body:** (all fields optional)
    ```json
    {
        "name": "Lucky Jr.",
        "weight_kg": 28.5,
        "breed": "Golden Retriever Mix",
        "in_medical": true,
        "profile_image": "https://example.com/new-image.jpg"
    }
    ```
    
    **Response:**
    ```json
    {
        "message": "Pet info updated"
    }
    ```
    """
    success = await update_pet_info(session, pet_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found or no changes made")
    return {"message": "Pet info updated"}

@router.delete("/{pet_id}", summary="Delete Pet", description="Soft delete a pet (marks as deleted)")
async def delete_pet_endpoint(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **DELETE /v1/pets/{pet_id} - Soft Delete Pet**
    
    Marks a pet as deleted (soft delete). The pet will no longer appear in lists.
    
    **Path Parameters:**
    - **pet_id**: Pet ID (integer)
    
    **Response:**
    ```json
    {
        "message": "Pet deleted successfully"
    }
    ```
    """
    success = await delete_pet(session, pet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"message": "Pet deleted successfully"}


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