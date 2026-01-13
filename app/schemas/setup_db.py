import pymongo
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

# Database Connection Configuration
# Ensure your MongoDB is running on this URI
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "pet_medic_db"

def setup_database():
    try:
        # connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        print(f"Connected to MongoDB: {DB_NAME}")

        # Define Validation Schemas
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
                        "user_id": {"bsonType": "objectId"}, 
                        "name": {"bsonType": "string"},
                        "species": {"bsonType": "string"},
                        "breed": {"bsonType": "string"},
                        "color": {"bsonType": "string"},
                        "gender": {"bsonType": "string"},
                        "birth_date": {"bsonType": "date"}, 
                        "weight_kg": {"bsonType": "double"}, 
                        "allergies": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "infecund": {"bsonType": "bool"},
                        "profile_image": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"}, 
                    }
                }
            },
            "DRUGS": { 
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "DRUGS",
                    "required": ["user_id", "pet_id", "name"],
                    "properties": {
                        "user_id": {"bsonType": "objectId"}, 
                        "pet_id": {"bsonType": "objectId"},  
                        "name": {"bsonType": "string"},
                        "notes": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "properties": {"bsonType": "string"},
                        "image_urls": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "dosage": {"bsonType": "string"}, 
                        "frequency": {"bsonType": "string"}, 
                        "status": {"bsonType": "string"},    
                        "reminder_time": {"bsonType": "array", "items": {"bsonType": "date"}},
                        "start_date": {"bsonType": "date"},
                        "end_date": {"bsonType": "date"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
            "PETS_RECORDS": { 
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "PETS_RECORDS",
                    "properties": {
                        "pet_id": {"bsonType": "objectId"}, 
                        "note": {"bsonType": "string"},
                        "images": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
            "APPOINTMENTS": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "APPOINTMENTS",
                    "properties": {
                        "pet_id": {"bsonType": "objectId"}, 
                        "user_id": {"bsonType": "objectId"}, 
                        "note": {"bsonType": "string"},
                        "appointment_date": {"bsonType": "date"},
                        "status": {"bsonType": "string"}, 
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
                        "pet_id": {"bsonType": "objectId"}, 
                        "user_id": {"bsonType": "objectId"}, 
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
            "DRUGS_NOTIFICATION": { 
                "$jsonSchema": {
                    "bsonType": "object",
                    "title": "DRUGS_NOTIFICATION",
                    "required": ["drug_id"],
                    "properties": {
                        "user_id": {"bsonType": "objectId"}, 
                        "drug_id": {"bsonType": "objectId"}, 
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
                        "user_id": {"bsonType": "string"}, 
                        "key_id": {"bsonType": "string"},
                        "token_type": {"bsonType": "string"},
                        "expires_in": {"bsonType": "date"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                    }
                }
            },
        }

        # Iterate to create collections or update validators
        for name, schema in collections_schemas.items():
            if name not in db.list_collection_names():
                # Create new collection with validator
                db.create_collection(name, validator=schema)
                print(f"Created collection: {name}")
            else:
                # Update existing collection validator
                db.command("collMod", name, validator=schema)
                print(f"Updated validator for: {name}")

        print("\nDatabase setup completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    setup_database()