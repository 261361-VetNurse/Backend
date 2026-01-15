import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import CollectionInvalid

# Database connection configuration (should match your .env file)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "pet_medic_db"

async def setup_database():
    try:
        # 1. Connect to MongoDB using Async
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        print(f"Connected to MongoDB: {DB_NAME} (Async)")

        # 2. Define schemas (field names and types have been updated)
        collections_schemas = {
            "USERS": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "USERS",
                    "required": ["fname", "lname"],
                    "properties": {
                        "fname": {"bsonType": "string"},
                        "lname": {"bsonType": "string"},
                        "contact": {
                            "bsonType": "object",
                            "properties": {
                                "phone": {"bsonType": "string"},
                                "line_id": {"bsonType": "string"},
                                "email": {"bsonType": "string"},
                            }
                        },
                        "address": {
                            "bsonType": "object",
                            "properties": {
                                "address_line1": {"bsonType": "string"},
                                "address_line2": {"bsonType": "string"},
                                "subdistrict": {"bsonType": "string"},
                                "district": {"bsonType": "string"},
                                "province": {"bsonType": "string"},
                                "postal_code": {"bsonType": "string"},
                                "country": {"bsonType": "string"},
                            }
                        },
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
            "PETS": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "PETS",
                    "required": ["user_id", "name"],
                    "properties": {
                        "user_id": {"bsonType": "objectId"},  # Fixed: users_id -> user_id
                        "name": {"bsonType": "string"},
                        "species": {"bsonType": "string"},
                        "breed": {"bsonType": "string"},
                        "color": {"bsonType": "string"},
                        "gender": {"bsonType": "string"},
                        "birth_date": {"bsonType": "date"},   # Fixed: string -> date
                        "weight_kg": {"bsonType": "double"},  # Fixed: string -> double
                        "allergies": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "infecund": {"bsonType": "bool"},
                        "profile_image": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},   # Fixed: timestamp -> date
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
            "MEDICINES": {  # Renamed from DRUGS/DRUGES
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "MEDICINES",
                    "required": ["user_id", "pet_id", "name"],
                    "properties": {
                        "user_id": {"bsonType": "objectId"},  # Fixed: users_id -> user_id
                        "pet_id": {"bsonType": "objectId"},   # Fixed: pets_id -> pet_id
                        "name": {"bsonType": "string"},
                        "notes": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "properties": {"bsonType": "string"},
                        "image_urls": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "dosage": {"bsonType": "string"},
                        "frequency": {
                            "bsonType": "string",
                            "enum": ["-1", "0", "1", "2", "3", "4", "5", "6"]  # -1=Daily, 0=Mon, 6=Sun
                        },
                        "status": {
                            "bsonType": "string",
                            "enum": ["TAKE", "STOP"]  # TAKE=Active, STOP=Stopped
                        },
                        "reminder_time": {"bsonType": "array", "items": {"bsonType": "date"}},
                        "start_date": {"bsonType": "date"},
                        "end_date": {"bsonType": "date"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},   # Fixed: update_at -> updated_at
                    }
                }
            },
            "PETS_RECORDS": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "PETS_RECORDS",
                    "properties": {
                        "pet_id": {"bsonType": "objectId"},   # Fixed: pets_id -> pet_id
                        "note": {"bsonType": "string"},
                        "images": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},   # Fixed: update_at -> updated_at
                    }
                }
            },
            "APPOINTMENTS": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "APPOINTMENTS",
                    "properties": {
                        "pet_id": {"bsonType": "objectId"},   # Fixed: pets_id -> pet_id
                        "user_id": {"bsonType": "objectId"},  # Fixed: users_id -> user_id
                        "note": {"bsonType": "string"},
                        "appointment_date": {"bsonType": "date"},
                        "status": {"bsonType": "string"},     # Pending Enum
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
            "APPOINTMENTS_NOTIFICATION": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "APPOINTMENTS_NOTIFICATION",
                    "required": ["pet_id", "user_id", "appointment_id"],
                    "properties": {
                        "pet_id": {"bsonType": "objectId"},   # Fixed: pets_id -> pet_id
                        "user_id": {"bsonType": "objectId"},  # Fixed: users_id -> user_id
                        "appointment_id": {"bsonType": "objectId"},
                        "title": {"bsonType": "string"},
                        "notification_at": {"bsonType": "date"},
                        "sending_status": {"bsonType": "string"},
                        "status": {"bsonType": "string"},
                        "sending_count": {"bsonType": "int"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
            "MEDICINES_NOTIFICATION": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "MEDICINES_NOTIFICATION",
                    "required": ["pet_id", "user_id", "medicine_id"],
                    "properties": {
                        "pet_id": {"bsonType": "objectId"},
                        "user_id": {"bsonType": "objectId"},     # Fixed: users_id -> user_id
                        "medicine_id": {"bsonType": "objectId"}, # Fixed: medicines_id -> medicine_id
                        "title": {"bsonType": "string"},
                        "notification_at": {"bsonType": "date"},
                        "sending_status": {"bsonType": "string"},
                        "status": {"bsonType": "string"},
                        "sending_count": {"bsonType": "int"},
                        "istaken": {"bsonType": "bool"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
            "JWT": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "JWT",
                    "properties": {
                        "access_token": {"bsonType": "string"},
                        "user_id": {"bsonType": "string"},    # Keeping string for flexibility
                        "key_id": {"bsonType": "string"},
                        "token_type": {"bsonType": "string"},
                        "expires_in": {"bsonType": "date"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},   # Fixed: update_at -> updated_at
                    }
                }
            },
        }

        # 3. Drop existing collections and data (Clean Start)
        print("\n🗑️  Dropping existing collections...")
        existing_collections = await db.list_collection_names()
        
        for name in collections_schemas.keys():
            if name in existing_collections:
                await db[name].drop()
                print(f"  - Dropped collection: {name}")
        print("✓ Old collections cleared\n")
        
        # 4. Create collections with validators
        print("Creating collections with validators...")
        for name, schema in collections_schemas.items():
            await db.create_collection(name, validator=schema)
            print(f"[OK] Created collection: {name}")

        print("\nDatabase setup completed successfully!")

    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Run async function
    asyncio.run(setup_database())