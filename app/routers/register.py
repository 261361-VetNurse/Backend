from fastapi import APIRouter, Depends, HTTPException
from app.schemas.register_schema import OwnerRegister, PetRegister
from app.services import user_service
from app.services.auth_dependency import get_current_user

router = APIRouter(tags=["Register"])

@router.post("/owner") 
async def register_owner_endpoint(
    data: OwnerRegister, 
    current_user: dict = Depends(get_current_user)
):
    success = await user_service.register_owner(str(current_user["_id"]), data)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {"message": "Owner registered successfully"}

@router.post("/pet")
async def register_pet_endpoint(
    data: PetRegister, 
    current_user: dict = Depends(get_current_user)
):
    pet_id = await user_service.register_new_pet(str(current_user["_id"]), data)
    return {"message": "Pet registered successfully", "pet_id": pet_id}