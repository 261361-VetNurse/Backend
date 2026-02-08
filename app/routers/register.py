from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.register_schema import OwnerRegister, PetRegister
from app.services.user_service_sql import register_owner, register_new_pet
from app.services.auth_dependency_sql import get_current_user
from app.database_sql import get_session

router = APIRouter(tags=["Registration"])

@router.post("/owner", summary="Register Owner Profile", description="Register owner profile information for current user") 
async def register_owner_endpoint(
    data: OwnerRegister, 
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **POST /v1/register/owner - Register Owner Profile**
    
    Register owner profile information (name, contact, address).
    Sets `is_registered = true` after successful registration.
    
    **Required fields:**
    - `first_name`, `last_name`
    - `phone`, `email`
    - `address_line1`, `subdistrict`, `district`, `province`, `postal_code`
    
    **Optional fields:**
    - `address_line2`
    
    **Request Body Example:**
    ```json
    {
        "first_name": "สมชาย",
        "last_name": "ใจดี",
        "phone": "0812345678",
        "email": "somchai@example.com",
        "address_line1": "123 ถนนสุขุมวิท",
        "address_line2": "แขวงคลองเตย",
        "subdistrict": "คลองเตย",
        "district": "คลองเตย",
        "province": "กรุงเทพมหานคร",
        "postal_code": "10110"
    }
    ```
    
    **Response:**
    ```json
    {
        "message": "Owner registered successfully"
    }
    ```
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
    **POST /v1/register/pet - Register New Pet**
    
    Register a new pet linked to the current user.
    
    **Required fields:**
    - `name`, `species`, `gender`, `birth_date`
    
    **Optional fields:**
    - `breed`, `color`, `weight_kg`, `infecund`, `in_medical`
    - `profile_image`, `previous_clinic`, `has_medical_history`
    
    **Request Body Example:**
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
        "pet_id": 1
    }
    ```
    """
    pet_id = await register_new_pet(session, current_user["user_id"], data)
    return {"message": "Pet registered successfully", "pet_id": pet_id}