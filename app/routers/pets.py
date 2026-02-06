from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.register_schema import PetRegister 
from app.services import user_service
from app.services.auth_dependency import get_current_user 
from app.schemas.pet_schema import AppointmentCreate, MedicalHistoryCreate, PetNoteCreate , PetUpdateSchema, MedicationCreate

router = APIRouter()

# API สำหรับดึงรายการสัตว์เลี้ยงทั้งหมด (My Pets Page)
@router.get("") 
async def get_my_pets(current_user: dict = Depends(get_current_user)):
    pets = await user_service.get_pets_by_owner(str(current_user["_id"]))
    return pets

# API สำหรับลงทะเบียนสัตว์เลี้ยงใหม่ (Register Pet)
@router.post("", status_code=201)
async def register_new_pet(
    data: PetRegister, 
    current_user: dict = Depends(get_current_user)
):
    """ลงทะเบียนสัตว์เลี้ยงใหม่และผูกกับ ID ของเจ้าของ"""
    pet_id = await user_service.register_new_pet(str(current_user["_id"]), data)
    return {"message": "Pet registered successfully", "pet_id": pet_id}

# API สำหรับหน้า Dashboard Home
@router.get("/dashboard/home")
async def get_home_dashboard(current_user: dict = Depends(get_current_user)):
    return await user_service.get_dashboard_data(str(current_user["_id"]))

@router.get("/{pet_id}")
async def get_pet_detail(pet_id: int, current_user: dict = Depends(get_current_user)): 
    pet = await user_service.get_pet_by_id(str(pet_id)) 
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

@router.patch("/{pet_id}")
async def update_pet(pet_id: int, data: PetUpdateSchema, current_user: dict = Depends(get_current_user)):
    success = await user_service.update_pet_info(str(pet_id), data)
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found or no changes made")
    return {"message": "Pet info updated"}

# เพิ่มนัดหมายใหม่ให้สัตว์เลี้ยง: POST /v1/pets/{pet_id}/appointments
@router.post("/{pet_id}/appointments")
async def create_pet_appointment(
    pet_id: str, 
    data: AppointmentCreate, 
    current_user: dict = Depends(get_current_user)
):
    appointment_id = await user_service.add_appointment(str(current_user["_id"]), pet_id, data)
    return {"message": "Appointment set successfully", "appointment_id": appointment_id}

# บันทึกอาการสัตว์เลี้ยง: POST /v1/pets/{pet_id}/symptoms
@router.post("/{pet_id}/symptoms")
async def record_pet_symptom(
    pet_id: str, 
    data: PetNoteCreate, 
    current_user: dict = Depends(get_current_user)
):
    note_id = await user_service.add_pet_note(pet_id, data)
    return {"message": "Symptom recorded successfully", "note_id": note_id}

#  API บันทึกการให้ยา 
@router.post("/{pet_id}/medications")
async def add_pet_medication(
    pet_id: str, 
    data: MedicationCreate, 
    current_user: dict = Depends(get_current_user)
):
    med_id = await user_service.add_medication(str(current_user["_id"]),pet_id, data)
    return {"message": "Medication added successfully", "medication_id": med_id}

# API ดึงประวัติการใช้ยา 
@router.get("/{pet_id}/medications")
async def get_pet_medications(pet_id: int, current_user: dict = Depends(get_current_user)):
    return await user_service.get_medications_by_pet(str(pet_id))


# API สำหรับดึงประวัติการรักษาทั้งหมดของสัตว์เลี้ยง
@router.get("/{pet_id}/medical-history")
async def get_pet_medical_history(
    pet_id: str, 
    current_user: dict = Depends(get_current_user)
):
    return await user_service.get_pet_medical_history(str(pet_id))

# แก้ไขสถานะยา 
@router.patch("/medications/{med_id}/status")
async def toggle_medication_status(
    med_id: int, 
    status: str, 
    note: str = None, 
    current_user: dict = Depends(get_current_user)
):
    # ตรวจสอบ status 
    if status not in ["active", "stop"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    success = await user_service.toggle_medication_status(str(med_id), status, note)
    if not success:
        raise HTTPException(status_code=404, detail="Medication not found")
    return {"message": f"Medication status updated to {status}"}

# ลบนัดหมาย 
@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    success = await user_service.delete_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted successfully"}

# ลบรายการยา 
@router.delete("/medications/{med_id}")
async def delete_medication(med_id: str, current_user: dict = Depends(get_current_user)):
    success = await user_service.delete_medication(med_id)
    if not success:
        raise HTTPException(status_code=404, detail="Medication not found")
    return {"message": "Medication deleted successfully"}

# ลบสัตว์เลี้ยง
@router.delete("/{pet_id}")
async def delete_pet(pet_id: int, current_user: dict = Depends(get_current_user)):
    success = await user_service.delete_pet(str(pet_id))
    if not success:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"message": "Pet deleted successfully"}

@router.post("/{pet_id}/medical-history")
async def add_user_medical_history(
    pet_id: str, 
    data: MedicalHistoryCreate, 
    current_user: dict = Depends(get_current_user)
):
    history_id = await user_service.add_medical_history(pet_id, data)
    return {"message": "Medical history recorded", "history_id": history_id}