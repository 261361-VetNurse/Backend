import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

# ==========================================
# 1. CONFIGURATION
# ==========================================
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "pets_medic_db"

# ==========================================
# 2. DEFINE SCHEMAS (VALIDATORS)
# ==========================================
schemas = {
    "USERS": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["line_id", "fname", "lname", "phone", "create_date"],
            "properties": {
                "line_id": {"bsonType": "string"},
                "fname": {"bsonType": "string"},
                "lname": {"bsonType": "string"},
                "gender": {"bsonType": "string", "enum": ["Male", "Female", "Other"]},
                "phone": {"bsonType": "string"},
                "email": {"bsonType": "string"},
                "address": {"bsonType": "object"},
                "create_date": {"bsonType": "date"},
                "update_date": {"bsonType": "date"}
            }
        }
    },
    "PETS": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "name", "species", "birth_date", "sex", "create_date"],
            "properties": {
                "user_id": {"bsonType": "objectId"},
                "image_url": {"bsonType": "string"},
                "name": {"bsonType": "string"},
                "species": {"bsonType": "string"},
                "breed": {"bsonType": "string"},
                "birth_date": {"bsonType": "date"},
                "sex": {"bsonType": "string", "enum": ["Male", "Female", "Unknown"]},
                "color": {"bsonType": "string"},
                "create_date": {"bsonType": "date"},
                "update_date": {"bsonType": "date"}
            }
        }
    },
    "NOTES": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["pet_id", "user_id", "symptom", "create_date"],
            "properties": {
                "pet_id": {"bsonType": "objectId"},
                "user_id": {"bsonType": "objectId"},
                "image_urls": {"bsonType": "array", "items": {"bsonType": "string"}},
                "symptom": {"bsonType": "string"},
                "relapse_date": {"bsonType": "date"},
                "create_date": {"bsonType": "date"},
                "update_date": {"bsonType": "date"}
            }
        }
    },
    "APPOINTMENTS": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["pet_id", "user_id", "date", "status", "create_date"],
            "properties": {
                "pet_id": {"bsonType": "objectId"},
                "user_id": {"bsonType": "objectId"},
                "location": {"bsonType": "string"},
                "date": {"bsonType": "date"},
                "status": {"bsonType": "string", "enum": ["pending", "confirmed", "completed", "cancelled"]},
                "note": {"bsonType": "string"},
                "create_date": {"bsonType": "date"},
                "update_date": {"bsonType": "date"}
            }
        }
    },
    "MEDICINES": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["pet_id", "drug_name", "dosage", "status", "next_dose_time"],
            "properties": {
                "pet_id": {"bsonType": "objectId"},
                "drug_name": {"bsonType": "string"},
                "dosage": {"bsonType": "string"},
                "indication": {"bsonType": "string"},
                "note": {"bsonType": "string"},
                "frequency_config": {
                    "bsonType": "object",
                    "properties": {
                        "type": {"bsonType": "string", "enum": ["interval", "specific_time"]},
                        "interval_hours": {"bsonType": "int"},
                        "time_slots": {"bsonType": "array", "items": {"bsonType": "string"}}
                    }
                },
                "start_date": {"bsonType": "date"},
                "end_date": {"bsonType": "date"},
                "next_dose_time": {"bsonType": "date"},
                "status": {"bsonType": "string", "enum": ["active", "completed", "cancelled"]},
                "create_date": {"bsonType": "date"},
                "update_date": {"bsonType": "date"}
            }
        }
    },
    "NOTIFICATIONS": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "type", "title", "message", "is_read", "create_date"],
            "properties": {
                "user_id": {"bsonType": "objectId"},
                "type": {"bsonType": "string", "enum": ["medicine", "appointment", "system"]},
                "title": {"bsonType": "string"},
                "message": {"bsonType": "string"},
                "related_id": {"bsonType": "objectId"},
                "is_read": {"bsonType": "bool"},
                "create_date": {"bsonType": "date"}
            }
        }
    },
    "JWT": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["token", "user_id", "type", "expires_at"],
            "properties": {
                "token": {"bsonType": "string"},
                "user_id": {"bsonType": "objectId"},
                "type": {"bsonType": "string", "enum": ["access", "refresh"]},
                "expires_at": {"bsonType": "date"},
                "create_date": {"bsonType": "date"}
            }
        }
    }
}

# ==========================================
# 3. ASYNC INITIALIZATION FUNCTION
# ==========================================
async def init_db():
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI)
    
    #Drop Database (Clean Start)
    print(f"Dropping database: {DB_NAME}...")
    await client.drop_database(DB_NAME)
    
    db = client[DB_NAME]
    print(f"Database '{DB_NAME}' created fresh.")

    # --- Create Collections with Validators ---
    print("Creating Collections & Validators...")
    for coll_name, schema in schemas.items():
        try:
            await db.create_collection(coll_name, validator=schema)
            print(f"   - Created: {coll_name}")
        except Exception as e:
            print(f"Error creating {coll_name}: {e}")

    # --- Create Indexes ---
    print("Creating Indexes...")
    
    # Users
    await db.USERS.create_index([("line_id", ASCENDING)], unique=True)
    await db.USERS.create_index([("email", ASCENDING)])
    
    # Pets
    await db.PETS.create_index([("user_id", ASCENDING)])
    
    # Appointments
    await db.APPOINTMENTS.create_index([("date", ASCENDING), ("status", ASCENDING)])
    await db.APPOINTMENTS.create_index([("user_id", ASCENDING)])
    
    # Medicines (Notification Logic)
    await db.MEDICINES.create_index([("status", ASCENDING), ("next_dose_time", ASCENDING)])
    await db.MEDICINES.create_index([("pet_id", ASCENDING)])
    
    # Notifications (NEW)
    # ค้นหาแจ้งเตือนของ User ที่ยังไม่อ่านได้เร็ว
    await db.NOTIFICATIONS.create_index([("user_id", ASCENDING), ("is_read", ASCENDING)]) 
    # เรียงลำดับเวลา (ใหม่ -> เก่า)
    await db.NOTIFICATIONS.create_index([("create_date", DESCENDING)]) 
    
    # JWT (Auto Expire)
    await db.JWT.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

    print("\n🎉 SUCCESS: Database initialization complete (Async)!")
    client.close()

# ==========================================
# 4. RUN SCRIPT
# ==========================================
if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"Fatal Error: {e}")