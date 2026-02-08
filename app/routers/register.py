from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.register_schema import OwnerRegister, PetRegister
from app.services.user_service_sql import register_owner, register_new_pet
from app.services.auth_dependency_sql import get_current_user
from app.database_sql import get_session

router = APIRouter(tags=["Registration 📝"])

@router.post("/owner", summary="Register Owner Profile", description="Register owner profile information for current user") 
async def register_owner_endpoint(
    data: OwnerRegister, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Register owner profile information
    
    **Required fields:**
    - first_name, last_name
    - phone, email
    - address information (line1, subdistrict, district, province, postal_code)
    """
    success = await register_owner(session, current_user["user_id"], data)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {"message": "Owner registered successfully"}

@router.post("/pet", summary="Register New Pet", description="Register new pet for current user")
async def register_pet_endpoint(
    data: PetRegister, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Register new pet for current user
    
    **Required fields:**
    - name, species, gender, birth_date
    
    **Optional fields:**
    - breed, color, weight_kg, infecund, profile_image, previous_clinic, has_medical_history
    """
    pet_id = await register_new_pet(session, current_user["user_id"], data)
    return {"message": "Pet registered successfully", "pet_id": pet_id}