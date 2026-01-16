"""
Generate Mock Data for Pet Medic Database
Creates 3 complete examples with all tables interconnected
"""

import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import random

# ==========================================
# CONFIGURATION
# ==========================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "pet_medic_db"

# ==========================================
# MOCK DATA GENERATOR
# ==========================================

class MockDataGenerator:
    def __init__(self, db):
        self.db = db
        self.user_ids = []
        self.pet_ids = []
        self.medicine_ids = []
        self.appointment_ids = []
        
    async def clear_all_data(self):
        """Clear all existing mock data"""
        print("\n🗑️  Clearing existing data...")
        collections = [
            "USERS", "PETS", "MEDICINES", "PETS_RECORDS", 
            "APPOINTMENTS", "APPOINTMENTS_NOTIFICATION", 
            "MEDICINES_NOTIFICATION", "JWT"
        ]
        
        for collection_name in collections:
            result = await self.db[collection_name].delete_many({})
            print(f"  - Deleted {result.deleted_count} documents from {collection_name}")
        print("✓ Old data cleared\n")
    
    async def generate_users(self):
        """Generate 3 users with complete information"""
        print("Generating 3 users...")
        
        users_data = [
            {
                "fname": "Somchai",
                "lname": "Raksatva",
                "contact": {
                    "phone": "0812345678",
                    "line_id": "LINE_somchai_001",
                    "email": "somchai@example.com"
                },
                "address": {
                    "address_line1": "123 Sukhumvit Road",
                    "address_line2": "Apt 501",
                    "subdistrict": "Khlong Toei",
                    "district": "Khlong Toei",
                    "province": "Bangkok",
                    "postal_code": "10110",
                    "country": "Thailand"
                },
                "created_at": datetime.utcnow() - timedelta(days=180),
                "updated_at": datetime.utcnow()
            },
            {
                "fname": "Pensri",
                "lname": "Meesuk",
                "contact": {
                    "phone": "0823456789",
                    "line_id": "LINE_pensri_002",
                    "email": "pensri@example.com"
                },
                "address": {
                    "address_line1": "456 Ratchada Road",
                    "address_line2": "",
                    "subdistrict": "Din Daeng",
                    "district": "Din Daeng",
                    "province": "Bangkok",
                    "postal_code": "10400",
                    "country": "Thailand"
                },
                "created_at": datetime.utcnow() - timedelta(days=150),
                "updated_at": datetime.utcnow()
            },
            {
                "fname": "Wichai",
                "lname": "Boonmee",
                "contact": {
                    "phone": "0834567890",
                    "line_id": "LINE_wichai_003",
                    "email": "wichai@example.com"
                },
                "address": {
                    "address_line1": "789 Rama IV Road",
                    "address_line2": "Building B, Floor 3",
                    "subdistrict": "Silom",
                    "district": "Bang Rak",
                    "province": "Bangkok",
                    "postal_code": "10500",
                    "country": "Thailand"
                },
                "created_at": datetime.utcnow() - timedelta(days=200),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await self.db.USERS.insert_many(users_data)
        self.user_ids = result.inserted_ids
        print(f"✓ Created {len(self.user_ids)} users")
        return self.user_ids
    
    async def generate_pets(self):
        """Generate 3 pets (1 pet per user)"""
        print("Generating 3 pets...")
        
        pets_data = [
            {
                "user_id": self.user_ids[0],
                "name": "Lucky",
                "species": "Dog",
                "breed": "Golden Retriever",
                "color": "Golden",
                "gender": "Male",
                "birth_date": datetime.utcnow() - timedelta(days=1095),  # 3 years old
                "weight_kg": 28.5,
                "allergies": ["Chicken", "Wheat"],
                "infecund": False,
                "profile_image": "https://images.dog.ceo/breeds/retriever-golden/n02099601_1003.jpg",
                "created_at": datetime.utcnow() - timedelta(days=180),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": self.user_ids[1],
                "name": "Momo",
                "species": "Cat",
                "breed": "Scottish Fold",
                "color": "Gray",
                "gender": "Female",
                "birth_date": datetime.utcnow() - timedelta(days=730),  # 2 years old
                "weight_kg": 4.2,
                "allergies": ["Dairy"],
                "infecund": True,
                "profile_image": "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg",
                "created_at": datetime.utcnow() - timedelta(days=150),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": self.user_ids[2],
                "name": "Cookie",
                "species": "Dog",
                "breed": "Corgi",
                "color": "Brown and White",
                "gender": "Female",
                "birth_date": datetime.utcnow() - timedelta(days=547),  # 1.5 years old
                "weight_kg": 12.8,
                "allergies": [],
                "infecund": False,
                "profile_image": "https://images.dog.ceo/breeds/corgi-cardigan/n02113186_8577.jpg",
                "created_at": datetime.utcnow() - timedelta(days=200),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await self.db.PETS.insert_many(pets_data)
        self.pet_ids = result.inserted_ids
        print(f"✓ Created {len(self.pet_ids)} pets")
        return self.pet_ids
    
    async def generate_medicines(self):
        """Generate medicines for all 3 pets"""
        print("Generating medicines for all pets...")
        
        medicines_data = [
            # Medicines for Lucky (Dog)
            {
                "user_id": self.user_ids[0],
                "pet_id": self.pet_ids[0],
                "name": "Amoxicillin",
                "notes": ["Take after meals", "Complete full course"],
                "properties": "Antibiotic for bacterial infections",
                "image_urls": ["https://via.placeholder.com/300x300?text=Amoxicillin"],
                "dosage": "500mg",
                "frequency": "twice_daily",
                "status": "active",
                "reminder_time": [
                    datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0),
                    datetime.utcnow().replace(hour=20, minute=0, second=0, microsecond=0)
                ],
                "start_date": datetime.utcnow() - timedelta(days=2),
                "end_date": datetime.utcnow() + timedelta(days=5),
                "created_at": datetime.utcnow() - timedelta(days=2),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": self.user_ids[0],
                "pet_id": self.pet_ids[0],
                "name": "Glucosamine",
                "notes": ["For joint health", "Long-term supplement"],
                "properties": "Joint supplement",
                "image_urls": ["https://via.placeholder.com/300x300?text=Glucosamine"],
                "dosage": "1 tablet",
                "frequency": "once_daily",
                "status": "active",
                "reminder_time": [
                    datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
                ],
                "start_date": datetime.utcnow() - timedelta(days=30),
                "end_date": datetime.utcnow() + timedelta(days=60),
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow()
            },
            # Medicines for Momo (Cat)
            {
                "user_id": self.user_ids[1],
                "pet_id": self.pet_ids[1],
                "name": "Prednisolone",
                "notes": ["Anti-inflammatory", "Do not stop suddenly"],
                "properties": "Corticosteroid for inflammation",
                "image_urls": ["https://via.placeholder.com/300x300?text=Prednisolone"],
                "dosage": "5mg",
                "frequency": "once_daily",
                "status": "active",
                "reminder_time": [
                    datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
                ],
                "start_date": datetime.utcnow() - timedelta(days=5),
                "end_date": datetime.utcnow() + timedelta(days=10),
                "created_at": datetime.utcnow() - timedelta(days=5),
                "updated_at": datetime.utcnow()
            },
            # Medicines for Cookie (Dog)
            {
                "user_id": self.user_ids[2],
                "pet_id": self.pet_ids[2],
                "name": "Deworming Tablet",
                "notes": ["Quarterly deworming schedule"],
                "properties": "Intestinal parasite treatment",
                "image_urls": ["https://via.placeholder.com/300x300?text=Deworming"],
                "dosage": "1 tablet",
                "frequency": "single_dose",
                "status": "completed",
                "reminder_time": [
                    datetime.utcnow() - timedelta(days=7)
                ],
                "start_date": datetime.utcnow() - timedelta(days=7),
                "end_date": datetime.utcnow() - timedelta(days=7),
                "created_at": datetime.utcnow() - timedelta(days=10),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": self.user_ids[2],
                "pet_id": self.pet_ids[2],
                "name": "Multivitamin",
                "notes": ["Daily vitamin supplement"],
                "properties": "Complete vitamin formula for dogs",
                "image_urls": ["https://via.placeholder.com/300x300?text=Multivitamin"],
                "dosage": "1 chewable tablet",
                "frequency": "once_daily",
                "status": "active",
                "reminder_time": [
                    datetime.utcnow().replace(hour=8, minute=30, second=0, microsecond=0)
                ],
                "start_date": datetime.utcnow() - timedelta(days=60),
                "end_date": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(days=60),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await self.db.MEDICINES.insert_many(medicines_data)
        self.medicine_ids = result.inserted_ids
        print(f"✓ Created {len(self.medicine_ids)} medicine records")
        return self.medicine_ids
    
    async def generate_pets_records(self):
        """Generate pet health records for all pets"""
        print("Generating pet records...")
        
        records_data = [
            # Records for Lucky
            {
                "pet_id": self.pet_ids[0],
                "note": "Annual health checkup completed. All vitals normal. Recommended joint supplement due to breed predisposition.",
                "images": [
                    "https://via.placeholder.com/400x300?text=Lucky+Checkup+1",
                    "https://via.placeholder.com/400x300?text=Lucky+Checkup+2"
                ],
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "pet_id": self.pet_ids[0],
                "note": "Ear infection detected. Started antibiotic treatment. Follow-up in 7 days.",
                "images": ["https://via.placeholder.com/400x300?text=Lucky+Ear+Infection"],
                "created_at": datetime.utcnow() - timedelta(days=2),
                "updated_at": datetime.utcnow() - timedelta(days=2)
            },
            # Records for Momo
            {
                "pet_id": self.pet_ids[1],
                "note": "Skin allergy symptoms observed. Started anti-inflammatory medication. Avoiding dairy products.",
                "images": [
                    "https://via.placeholder.com/400x300?text=Momo+Skin+Issue"
                ],
                "created_at": datetime.utcnow() - timedelta(days=5),
                "updated_at": datetime.utcnow() - timedelta(days=5)
            },
            {
                "pet_id": self.pet_ids[1],
                "note": "Vaccination update: Rabies vaccine administered. Next due in 1 year.",
                "images": [],
                "created_at": datetime.utcnow() - timedelta(days=90),
                "updated_at": datetime.utcnow() - timedelta(days=90)
            },
            # Records for Cookie
            {
                "pet_id": self.pet_ids[2],
                "note": "6-month checkup. Weight gain on track. Deworming completed successfully.",
                "images": [
                    "https://via.placeholder.com/400x300?text=Cookie+Checkup"
                ],
                "created_at": datetime.utcnow() - timedelta(days=7),
                "updated_at": datetime.utcnow() - timedelta(days=7)
            }
        ]
        
        result = await self.db.PETS_RECORDS.insert_many(records_data)
        print(f"✓ Created {len(records_data)} pet records")
        return result.inserted_ids
    
    async def generate_appointments(self):
        """Generate appointments for all pets"""
        print("Generating appointments...")
        
        appointments_data = [
            # Appointments for Lucky
            {
                "pet_id": self.pet_ids[0],
                "user_id": self.user_ids[0],
                "note": "Follow-up checkup for ear infection",
                "appointment_date": datetime.utcnow() + timedelta(days=5, hours=10),
                "status": "confirmed",
                "created_at": datetime.utcnow() - timedelta(days=2),
                "updated_at": datetime.utcnow()
            },
            {
                "pet_id": self.pet_ids[0],
                "user_id": self.user_ids[0],
                "note": "Annual vaccination due",
                "appointment_date": datetime.utcnow() + timedelta(days=30, hours=14),
                "status": "pending",
                "created_at": datetime.utcnow() - timedelta(days=1),
                "updated_at": datetime.utcnow()
            },
            # Appointments for Momo
            {
                "pet_id": self.pet_ids[1],
                "user_id": self.user_ids[1],
                "note": "Skin allergy follow-up consultation",
                "appointment_date": datetime.utcnow() + timedelta(days=10, hours=11),
                "status": "confirmed",
                "created_at": datetime.utcnow() - timedelta(days=3),
                "updated_at": datetime.utcnow()
            },
            {
                "pet_id": self.pet_ids[1],
                "user_id": self.user_ids[1],
                "note": "Dental cleaning scheduled",
                "appointment_date": datetime.utcnow() + timedelta(days=45, hours=9),
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            # Appointments for Cookie
            {
                "pet_id": self.pet_ids[2],
                "user_id": self.user_ids[2],
                "note": "Spaying procedure scheduled",
                "appointment_date": datetime.utcnow() + timedelta(days=20, hours=8),
                "status": "confirmed",
                "created_at": datetime.utcnow() - timedelta(days=5),
                "updated_at": datetime.utcnow()
            },
            # Past appointment (completed)
            {
                "pet_id": self.pet_ids[2],
                "user_id": self.user_ids[2],
                "note": "6-month health checkup",
                "appointment_date": datetime.utcnow() - timedelta(days=7, hours=10),
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=15),
                "updated_at": datetime.utcnow() - timedelta(days=7)
            }
        ]
        
        result = await self.db.APPOINTMENTS.insert_many(appointments_data)
        self.appointment_ids = result.inserted_ids
        print(f"✓ Created {len(self.appointment_ids)} appointments")
        return self.appointment_ids
    
    async def generate_appointments_notifications(self):
        """Generate appointment notifications"""
        print("Generating appointment notifications...")
        
        notifications_data = [
            {
                "pet_id": self.pet_ids[0],
                "user_id": self.user_ids[0],
                "appointment_id": self.appointment_ids[0],
                "title": "Upcoming Appointment: Follow-up checkup",
                "notification_at": datetime.utcnow() + timedelta(days=4, hours=10),
                "sending_status": "scheduled",
                "status": "pending",
                "sending_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "pet_id": self.pet_ids[1],
                "user_id": self.user_ids[1],
                "appointment_id": self.appointment_ids[2],
                "title": "Reminder: Skin allergy follow-up tomorrow",
                "notification_at": datetime.utcnow() + timedelta(days=9, hours=10),
                "sending_status": "scheduled",
                "status": "pending",
                "sending_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "pet_id": self.pet_ids[2],
                "user_id": self.user_ids[2],
                "appointment_id": self.appointment_ids[4],
                "title": "Important: Spaying procedure in 5 days",
                "notification_at": datetime.utcnow() + timedelta(days=15, hours=9),
                "sending_status": "scheduled",
                "status": "pending",
                "sending_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await self.db.APPOINTMENTS_NOTIFICATION.insert_many(notifications_data)
        print(f"✓ Created {len(notifications_data)} appointment notifications")
        return result.inserted_ids
    
    async def generate_medicines_notifications(self):
        """Generate medicine notifications"""
        print("Generating medicine notifications...")
        
        notifications_data = [
            # Notifications for Lucky's medicines
            {
                "pet_id": self.pet_ids[0],
                "user_id": self.user_ids[0],
                "medicine_id": self.medicine_ids[0],
                "title": "Time to give Amoxicillin",
                "notification_at": datetime.utcnow() + timedelta(hours=2),
                "sending_status": "scheduled",
                "status": "pending",
                "sending_count": 0,
                "istaken": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "pet_id": self.pet_ids[0],
                "user_id": self.user_ids[0],
                "medicine_id": self.medicine_ids[1],
                "title": "Daily Glucosamine reminder",
                "notification_at": datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1),
                "sending_status": "scheduled",
                "status": "pending",
                "sending_count": 0,
                "istaken": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            # Notification for Momo's medicine
            {
                "pet_id": self.pet_ids[1],
                "user_id": self.user_ids[1],
                "medicine_id": self.medicine_ids[2],
                "title": "Prednisolone - Morning dose",
                "notification_at": datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1),
                "sending_status": "scheduled",
                "status": "pending",
                "sending_count": 0,
                "istaken": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            # Notification for Cookie's medicine (past notification - already taken)
            {
                "pet_id": self.pet_ids[2],
                "user_id": self.user_ids[2],
                "medicine_id": self.medicine_ids[4],
                "title": "Morning Multivitamin",
                "notification_at": datetime.utcnow() - timedelta(hours=2),
                "sending_status": "sent",
                "status": "completed",
                "sending_count": 1,
                "istaken": True,
                "created_at": datetime.utcnow() - timedelta(hours=3),
                "updated_at": datetime.utcnow() - timedelta(hours=1)
            }
        ]
        
        result = await self.db.MEDICINES_NOTIFICATION.insert_many(notifications_data)
        print(f"✓ Created {len(notifications_data)} medicine notifications")
        return result.inserted_ids
    
    async def generate_jwt_tokens(self):
        """Generate JWT tokens for users"""
        print("Generating JWT tokens...")
        
        tokens_data = [
            {
                "access_token": f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user_{str(self.user_ids[0])}",
                "user_id": str(self.user_ids[0]),
                "key_id": f"key_{random.randint(10000, 99999)}",
                "token_type": "Bearer",
                "expires_in": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(hours=1),
                "updated_at": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "access_token": f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user_{str(self.user_ids[1])}",
                "user_id": str(self.user_ids[1]),
                "key_id": f"key_{random.randint(10000, 99999)}",
                "token_type": "Bearer",
                "expires_in": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(hours=2),
                "updated_at": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "access_token": f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user_{str(self.user_ids[2])}",
                "user_id": str(self.user_ids[2]),
                "key_id": f"key_{random.randint(10000, 99999)}",
                "token_type": "Bearer",
                "expires_in": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(minutes=30),
                "updated_at": datetime.utcnow() - timedelta(minutes=30)
            }
        ]
        
        result = await self.db.JWT.insert_many(tokens_data)
        print(f"✓ Created {len(tokens_data)} JWT tokens")
        return result.inserted_ids

# ==========================================
# MAIN FUNCTION
# ==========================================

async def generate_all_mock_data():
    """Generate complete interconnected mock data"""
    print("="*60)
    print("Starting Mock Data Generation (3 Complete Examples)")
    print("="*60)
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    generator = MockDataGenerator(db)
    
    # Clear existing data
    await generator.clear_all_data()
    
    # Generate data in proper order (respecting foreign key relationships)
    print("Generating interconnected data...\n")
    await generator.generate_users()
    await generator.generate_pets()
    await generator.generate_medicines()
    await generator.generate_pets_records()
    await generator.generate_appointments()
    await generator.generate_appointments_notifications()
    await generator.generate_medicines_notifications()
    await generator.generate_jwt_tokens()
    
    print("\n" + "="*60)
    print("🎉 Mock Data Generation Complete!")
    print("="*60)
    
    # Print summary
    print("\n📊 Database Summary:")
    print(f"  Users:                      {await db.USERS.count_documents({})}")
    print(f"  Pets:                       {await db.PETS.count_documents({})}")
    print(f"  Medicines:                  {await db.MEDICINES.count_documents({})}")
    print(f"  Pet Records:                {await db.PETS_RECORDS.count_documents({})}")
    print(f"  Appointments:               {await db.APPOINTMENTS.count_documents({})}")
    print(f"  Appointment Notifications:  {await db.APPOINTMENTS_NOTIFICATION.count_documents({})}")
    print(f"  Medicine Notifications:     {await db.MEDICINES_NOTIFICATION.count_documents({})}")
    print(f"  JWT Tokens:                 {await db.JWT.count_documents({})}")
    
    print("\n✨ All data is interconnected:")
    print("  - Each user has 1 pet")
    print("  - Each pet has medicines, records, and appointments")
    print("  - All appointments have notifications")
    print("  - All active medicines have notifications")
    print("  - All users have valid JWT tokens")
    
    client.close()

# ==========================================
# RUN SCRIPT
# ==========================================

if __name__ == "__main__":
    try:
        asyncio.run(generate_all_mock_data())
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()