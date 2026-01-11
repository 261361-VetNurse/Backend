import time
from app.database import get_database
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from app.schemas.register_schema import OwnerRegister, PetRegister 
from app.schemas.pet_schema import AppointmentCreate, MedicalHistoryCreate, PetNoteCreate, PetUpdateSchema , MedicationCreate

async def register_owner(user_id: str, owner_data: OwnerRegister):
    db = get_database()

    update_data = owner_data.dict()
    update_data["is_registered"] = True
    update_data["updated_at"] = int(time.time())

    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0


# ฟังก์ชันสำหรับดึงรายการสัตว์เลี้ยง (My Pets Page)
async def get_pets_by_owner(owner_id: str):
    db = get_database()

    cursor = db["pets"].find({"user_id": owner_id, "is_deleted": False})
    pets = await cursor.to_list(length=100)
    
    for pet in pets:
        pet["_id"] = str(pet["_id"])
    return pets

# ฟังก์ชันสำหรับลงทะเบียนสัตว์เลี้ยงใหม่
async def register_new_pet(user_id: str, pet_data: PetRegister):
    db = get_database()
    new_pet = pet_data.dict()
    new_pet.update({
        "user_id": user_id,  
        "is_verified": False, 
        "is_deleted": False,
        "created_at": int(time.time())
    })
    result = await db["pets"].insert_one(new_pet)
    return str(result.inserted_id)

# ฟังก์ชันบันทึกนัดหมาย
async def add_appointment(user_id: str, pet_id: str, data: AppointmentCreate):
    db = get_database()
    new_doc = data.dict()
    new_doc.update({
        "user_id": user_id,
        "pet_id": pet_id, 
        "created_at": int(time.time())
    })
    result = await db["appointments"].insert_one(new_doc)
    return str(result.inserted_id)

# ฟังก์ชันบันทึกอาการสัตว์เลี้ยง
async def add_pet_note(pet_id: str, data: PetNoteCreate):
    db = get_database()
    new_note = data.dict()
    new_note.update({
        "pet_id": pet_id,
        "timestamp": int(time.time())
    })
    result = await db["pet_notes"].insert_one(new_note)
    return str(result.inserted_id)

# ฟังก์ชันดึงข้อมูลสัตว์เลี้ยงรายตัว
async def get_pet_by_id(pet_id: str):
    db = get_database()
    pet = await db["pets"].find_one({"_id": ObjectId(pet_id), "is_deleted": False})
    if pet:
        pet["_id"] = str(pet["_id"])
    return pet

async def delete_pet(pet_id: str):
    db = get_database()
    try:
        result = await db["pets"].update_one(
            {"_id": ObjectId(pet_id)},
            {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# ฟังก์ชันอัปเดตข้อมูลสัตว์เลี้ยง
async def update_pet_info(pet_id: str, data: PetUpdateSchema):
    db = get_database()
    update_data = {k: v for k, v in data.dict().items() if v is not None} 
    if not update_data:
        return False
    
    result = await db["pets"].update_one(
        {"_id": ObjectId(pet_id)},
        {"$set": update_data}
    )
    return result.matched_count > 0

# บันทึกประวัติยาใหม่
async def add_medication(user_id: str,pet_id: str, data: MedicationCreate):
    db = get_database()
    new_med = data.dict()
    new_med.update({
        "user_id": user_id,
        "pet_id": pet_id,
        "created_at": int(time.time()),
        "status": "active",
        "is_deleted": False
    })
    result = await db["medications"].insert_one(new_med)
    return str(result.inserted_id)

# ดึงประวัติยาทั้งหมดของสัตว์เลี้ยงตัวนั้น
async def get_medications_by_pet(pet_id: str):
    db = get_database()
    cursor = db["medications"].find({"pet_id": pet_id, "is_deleted": False})
    meds = await cursor.to_list(length=100)
    for med in meds:
        med["_id"] = str(med["_id"])
    return meds

async def get_pet_medical_history(pet_id: str):
    db = get_database()
    cursor = db["pet_notes"].find({"pet_id": pet_id}).sort("timestamp", -1)
    history = await cursor.to_list(length=100)
    for entry in history:
        entry["_id"] = str(entry["_id"])
    return history

async def toggle_medication_status(med_id: str, status: str, note: str = None):
    db = get_database()
    update_data = {"status": status}

    # ถ้าสถานะเป็น stop ต้องมีการบันทึก note ลงใน  notes_id
    if status == "stop" and note:
        update_data["note"] = note 
    result = await db["medications"].update_one(
        {"_id": ObjectId(med_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def get_dashboard_data(user_id: str):
    db = get_database()

    pets_cursor = db["pets"].find({"user_id": user_id, "is_deleted": False}).limit(10)
    pets = await pets_cursor.to_list(length=10)

    appointments_cursor = db["appointments"].find({
        "user_id": user_id, 
        "status": "upcoming",
        "is_deleted": {"$ne": True} 
    }).sort("appointment_date", 1).limit(5)

    medications_cursor = db["medications"].find({
        "user_id": user_id, 
        "status": "active",
        "is_deleted": {"$ne": True} 
    }).limit(5)

    appointments = await appointments_cursor.to_list(length=5)
    medications = await medications_cursor.to_list(length=5)

    for item in pets + appointments + medications:
        item["_id"] = str(item["_id"])

    return {
        "my_pets": pets,
        "upcoming_appointments": appointments,
        "active_medications": medications
    }

async def add_medical_history(pet_id: str, data: MedicalHistoryCreate):
    db = get_database()
    new_history = data.dict()
    new_history.update({
        "pet_id": pet_id,
        "type": "user_record", 
        "timestamp": int(time.time())
    })
    result = await db["pet_notes"].insert_one(new_history)
    return str(result.inserted_id)

# เพิ่มฟังก์ชันสำหรับ Soft Delete 
async def delete_appointment(appointment_id: str):
    db = get_database()
    result = await db["appointments"].update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {"is_deleted": True}}
    )
    return result.modified_count > 0

async def delete_medication(med_id: str):
    db = get_database()
    result = await db["medications"].update_one(
        {"_id": ObjectId(med_id)},
        {"$set": {"is_deleted": True}}
    )
    return result.modified_count > 0