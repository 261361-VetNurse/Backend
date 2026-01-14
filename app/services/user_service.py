import time
import random
from app.database import get_database
from datetime import datetime
from bson import ObjectId
from app.schemas.register_schema import OwnerRegister, PetRegister 
from app.schemas.pet_schema import AppointmentCreate, MedicalHistoryCreate, PetNoteCreate, PetUpdateSchema , MedicationCreate

# ISO Format
def format_timestamp(timestamp: int):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

async def generate_unique_id(collection_name: str, prefix: int):
    db = get_database()
    while True:
        # สุ่มเลข 5 หลักหลังต่อจาก Prefix (เช่น 2 + 12345 = 212345)
        new_id = int(f"{prefix}{random.randint(10000, 99999)}")
        # เช็คว่า ID นี้ซ้ำไหม
        exists = await db[collection_name].find_one({"_id": new_id})
        if not exists:
            return new_id
        
async def register_owner(user_id: str, owner_data: OwnerRegister):
    db = get_database()
    update_data = owner_data.model_dump()
    update_data.update({"is_registered": True, "updated_at": int(time.time())})
    result = await db["users"].update_one({"_id": int(user_id)}, {"$set": update_data})
    return result.modified_count > 0

# ฟังก์ชันสำหรับดึงรายการสัตว์เลี้ยง (My Pets Page)
async def get_pets_by_owner(owner_id: str):
    db = get_database()
    cursor = db["pets"].find({"user_id": int(owner_id), "is_deleted": False})
    pets = await cursor.to_list(length=100)
    for pet in pets:
        pet["_id"] = str(pet["_id"])
        if "created_at" in pet:
            pet["created_at"] = format_timestamp(pet["created_at"])
    return pets

# ฟังก์ชันสำหรับลงทะเบียนสัตว์เลี้ยงใหม่
async def register_new_pet(user_id: str, pet_data: PetRegister):
    db = get_database()
    pet_id = await generate_unique_id("pets", 2)
    
    new_pet = pet_data.model_dump()
    new_pet.update({
        "_id": pet_id, 
        "user_id": int(user_id),  
        "is_verified": False, 
        "is_deleted": False,
        "created_at": int(time.time())
    })
    await db["pets"].insert_one(new_pet)
    return pet_id

# ฟังก์ชันบันทึกนัดหมาย
async def add_appointment(user_id: str, pet_id: str, data: AppointmentCreate):
    db = get_database()
    appt_id = await generate_unique_id("appointments", 3)
    new_doc = data.model_dump()
    new_doc.update({
        "_id": appt_id,
        "user_id": int(user_id),
        "pet_id": int(pet_id), 
        "created_at": int(time.time()),
        "is_deleted": False
    })
    await db["appointments"].insert_one(new_doc)
    return appt_id


# ฟังก์ชันบันทึกอาการสัตว์เลี้ยง
async def add_pet_note(pet_id: str, data: PetNoteCreate):
    db = get_database()
    note_id = await generate_unique_id("pet_notes", 5)
    new_note = data.model_dump()
    new_note.update({
        "_id": note_id,
        "pet_id": int(pet_id),
        "timestamp": int(time.time())
    })
    await db["pet_notes"].insert_one(new_note)
    return note_id

# ฟังก์ชันดึงข้อมูลสัตว์เลี้ยงรายตัว
async def get_pet_by_id(pet_id: str):
    db = get_database()
    pet = await db["pets"].find_one({"_id": int(pet_id), "is_deleted": False})
    if pet:
        pet["_id"] = str(pet["_id"])
        if "created_at" in pet:
            pet["created_at"] = format_timestamp(pet["created_at"])
    return pet

async def delete_pet(pet_id: str):
    db = get_database()
    result = await db["pets"].update_one(
        {"_id": int(pet_id)},
        {"$set": {"is_deleted": True}}
    )
    return result.modified_count > 0

# ฟังก์ชันอัปเดตข้อมูลสัตว์เลี้ยง
async def update_pet_info(pet_id: str, data: PetUpdateSchema):
    db = get_database()
    update_data = {k: v for k, v in data.dict().items() if v is not None} 
    if not update_data:
        return False
    
    result = await db["pets"].update_one(
        {"_id": int(pet_id)},
        {"$set": update_data}
    )
    return result.matched_count > 0

# บันทึกประวัติยาใหม่
async def add_medication(user_id: str, pet_id: str, data: MedicationCreate):
    db = get_database()
    med_id = await generate_unique_id("medications", 4)
    
    new_med = data.model_dump()
    new_med.update({
        "_id": med_id,
        "user_id": int(user_id),
        "pet_id": int(pet_id),
        "created_at": int(time.time()),
        "status": "active",
        "is_deleted": False
    })
    await db["medications"].insert_one(new_med)
    return med_id

# ดึงประวัติยาทั้งหมดของสัตว์เลี้ยงตัวนั้น
async def get_medications_by_pet(pet_id: str):
    db = get_database()
    cursor = db["medications"].find({"pet_id": int(pet_id), "is_deleted": False})
    meds = await cursor.to_list(length=100)
    for med in meds:
        med["_id"] = str(med["_id"])
        if "created_at" in med:
            med["created_at"] = format_timestamp(med["created_at"])
    return meds

async def get_pet_medical_history(pet_id: str):
    db = get_database()
    cursor = db["pet_notes"].find({"pet_id": int(pet_id)}).sort("timestamp", -1)
    history = await cursor.to_list(length=100)
    for entry in history:
        entry["_id"] = str(entry["_id"])
        if "timestamp" in entry:
            entry["timestamp"] = format_timestamp(entry["timestamp"])
    return history

async def toggle_medication_status(med_id: str, status: str, note_text: str = None):
    db = get_database()
    update_data = {"status": status}
    
    med_info = await db["medications"].find_one({"_id": int(med_id)})
    if not med_info:
        return False

    if status == "stop" and note_text:
        note_id = await generate_unique_id("pet_notes", 5)
        
        pet_id_int = int(med_info["pet_id"]) 
        
        new_note = {
            "_id": note_id,
            "pet_id": pet_id_int, 
            "note": f"หยุดยา {med_info['drug_name']}: {note_text}",
            "tags": ["หยุดยา"],
            "timestamp": int(time.time()) 
        }
        await db["pet_notes"].insert_one(new_note)
        
        update_data["notes_id"] = str(note_id)

    # อัปเดตข้อมูลยา
    result = await db["medications"].update_one(
        {"_id": int(med_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def get_dashboard_data(user_id: str):
    db = get_database()
    uid = int(user_id) 

    pets = await db["pets"].find({"user_id": uid, "is_deleted": False}).to_list(10)
    
    appointments = await db["appointments"].find({
        "user_id": uid, "status": "upcoming", "is_deleted": {"$ne": True} 
    }).sort("appointment_date", 1).to_list(5)

    medications = await db["medications"].find({
        "user_id": uid, "status": "active", "is_deleted": {"$ne": True} 
    }).to_list(5)

    for item in pets + appointments + medications:
        item["_id"] = str(item["_id"])


        if "created_at" in item and isinstance(item["created_at"], int):
            item["created_at"] = format_timestamp(item["created_at"])
            
        if "created_at" in item and isinstance(item["created_at"], int) and item.get("_id", "").startswith("3"):
             item["created_at"] = format_timestamp(item["created_at"])

    return {
        "my_pets": pets,
        "upcoming_appointments": appointments,
        "active_medications": medications
    }

async def add_medical_history(pet_id: str, data: MedicalHistoryCreate):
    db = get_database()
    new_history = data.model_dump()
    new_history.update({
        "pet_id": int(pet_id),
        "type": "user_record", 
        "timestamp": int(time.time())
    })
    result = await db["pet_notes"].insert_one(new_history)
    return str(result.inserted_id)

# เพิ่มฟังก์ชันสำหรับ Soft Delete 
async def delete_appointment(appointment_id: str):
    db = get_database()
    result = await db["appointments"].update_one(
        {"_id": int(appointment_id)},
        {"$set": {"is_deleted": True}}
    )
    return result.modified_count > 0

async def delete_medication(med_id: str):
    db = get_database()
    result = await db["medications"].update_one(
        {"_id": int(med_id)},
        {"$set": {"is_deleted": True}}
    )
    return result.modified_count > 0