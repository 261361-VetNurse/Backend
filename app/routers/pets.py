from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.register_schema import PetRegister 
from app.services.user_service_sql import (
    get_pets_by_owner, register_new_pet, get_pet_by_id, 
    update_pet_info, delete_pet, add_pet_record, get_pet_records
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
    """Return list of all active (non-deleted) pets owned by the current user."""
    pets = await get_pets_by_owner(session, current_user["user_id"])
    return pets

@router.post("", status_code=201, summary="Register New Pet", description="Register a new pet for current user")
async def register_new_pet_endpoint(
    data: PetRegister, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Register a new pet and link it to the current user."""
    pet_id = await register_new_pet(session, current_user["user_id"], data)
    return {"message": "Pet registered successfully", "pet_id": pet_id}

@router.get("/{pet_id}", summary="Get Pet Detail", description="Get detailed pet information by ID")
async def get_pet_detail(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
): 
    """Get detailed information about a specific pet. Returns 404 if not found or soft-deleted."""
    pet = await get_pet_by_id(session, pet_id, current_user["user_id"])
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
    """Partial update for pet information. Returns 404 if not found."""
    success = await update_pet_info(session, pet_id, current_user["user_id"], data)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found or no changes made")
    return {"message": "Pet info updated"}

@router.delete("/{pet_id}", summary="Delete Pet", description="Soft delete a pet (marks as deleted)")
async def delete_pet_endpoint(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Soft-delete a pet so it no longer appears in lists."""
    success = await delete_pet(session, pet_id, current_user["user_id"])
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
    try:
        note_id = await add_pet_record(session, pet_id, current_user["user_id"], data.note, data.images if hasattr(data, 'images') else None)
    except ValueError:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"message": "Symptom recorded successfully", "note_id": note_id}

@router.get("/{pet_id}/medical-history")
async def get_pet_medical_history_endpoint(
    pet_id: int, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all medical history/records for a pet"""
    records = await get_pet_records(session, pet_id, current_user["user_id"])
    if records is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return records

@router.post("/{pet_id}/medical-history")
async def add_user_medical_history(
    pet_id: int, 
    data: MedicalHistoryCreate, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add medical history record"""
    try:
        history_id = await add_pet_record(session, pet_id, current_user["user_id"], data.note, data.images if hasattr(data, 'images') else None)
    except ValueError:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"message": "Medical history recorded", "history_id": history_id}