"""
Seed Mock Data for Dashboard Testing

This script populates the MongoDB database with mock data for testing:
- Mock user
- Mock JWT token (mock_token_user_1_long_live)
- Mock pets
- Mock medicine notifications for today
- Mock appointments
"""

import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

async def seed_mock_data():
    """Seed the database with mock data"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    
    # 1. Find existing TestUser1
    print("\n1. Looking for existing TestUser1...")
    existing_user = await db.USERS.find_one({"fname": "TestUser1"})
    
    if not existing_user:
        print("   ❌ ERROR: TestUser1 not found in database!")
        print("   Please make sure TestUser1 exists in the USERS collection")
        client.close()
        return
    
    mock_user_id = existing_user["_id"]
    print(f"   ✓ Found TestUser1 with ID: {mock_user_id}")
    print(f"   - Name: {existing_user['fname']} {existing_user.get('lname', '')}")
    print(f"   - Line ID: {existing_user.get('line_id', 'N/A')}")
    
    # 2. Create/Update mock JWT token
    print("\n2. Creating mock JWT token...")
    token = "mock_token_user_1_long_live"
    existing_token = await db.JWT.find_one({"access_token": token})
    
    # Token expires in 365 days
    expires_at = datetime.utcnow() + timedelta(days=365)
    
    if existing_token:
        # Update existing token
        await db.JWT.update_one(
            {"access_token": token},
            {"$set": {
                "user_id": str(mock_user_id),
                "expires_in": expires_at,
                "updated_at": datetime.utcnow()
            }}
        )
        print(f"   ✓ Updated existing JWT token (expires: {expires_at})")
    else:
        # Create new token
        jwt_data = {
            "access_token": token,
            "user_id": str(mock_user_id),
            "token_type": "Bearer",
            "expires_in": expires_at,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.JWT.insert_one(jwt_data)
        print(f"   ✓ Created JWT token (expires: {expires_at})")
    
    # 3. Create mock pets
    print("\n3. Creating mock pets...")
    pet_names = ["Luna", "Max", "Bella"]
    pet_ids = []
    
    for i, pet_name in enumerate(pet_names):
        existing_pet = await db.PETS.find_one({
            "user_id": mock_user_id,
            "name": pet_name
        })
        
        if existing_pet:
            print(f"   ✓ Pet '{pet_name}' already exists")
            pet_ids.append(existing_pet["_id"])
        else:
            pet_id = ObjectId()
            pet_data = {
                "_id": pet_id,
                "user_id": mock_user_id,
                "name": pet_name,
                "species": "dog" if i % 2 == 0 else "cat",
                "breed": "Golden Retriever" if i % 2 == 0 else "Persian",
                "age": 3 + i,
                "weight": 20.5 + i * 5,
                "profile_image": f"https://via.placeholder.com/150?text={pet_name}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.PETS.insert_one(pet_data)
            pet_ids.append(pet_id)
            print(f"   ✓ Created pet '{pet_name}' (ID: {pet_id})")
    
    # 4. Create mock medicines
    print("\n4. Creating mock medicines...")
    medicine_names = ["Antibiotics", "Pain Relief", "Vitamins"]
    medicine_ids = []
    
    for medicine_name in medicine_names:
        existing_medicine = await db.MEDICINES.find_one({"name": medicine_name})
        
        if existing_medicine:
            print(f"   ✓ Medicine '{medicine_name}' already exists")
            medicine_ids.append(existing_medicine["_id"])
        else:
            medicine_id = ObjectId()
            medicine_data = {
                "_id": medicine_id,
                "name": medicine_name,
                "description": f"{medicine_name} for pets",
                "created_at": datetime.utcnow()
            }
            await db.MEDICINES.insert_one(medicine_data)
            medicine_ids.append(medicine_id)
            print(f"   ✓ Created medicine '{medicine_name}' (ID: {medicine_id})")
    
    # 5. Create medicine notifications for today
    print("\n5. Creating medicine notifications for today...")
    
    # Delete old notifications for this user
    delete_result = await db.MEDICINES_NOTIFICATION.delete_many({"user_id": mock_user_id})
    print(f"   ✓ Deleted {delete_result.deleted_count} old notifications")
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    notification_times = [
        today.replace(hour=8, minute=0),
        today.replace(hour=14, minute=0),
        today.replace(hour=20, minute=0)
    ]
    
    for i, notif_time in enumerate(notification_times):
        pet_id = pet_ids[i % len(pet_ids)]
        medicine_id = medicine_ids[i % len(medicine_ids)]
        
        notification_data = {
            "_id": ObjectId(),
            "user_id": mock_user_id,
            "pet_id": pet_id,
            "medicine_id": medicine_id,
            "title": f"Medicine Reminder - {medicine_names[i % len(medicine_names)]}",
            "notification_at": notif_time,
            "status": "pending",
            "istaken": False,
            "created_at": datetime.utcnow()
        }
        await db.MEDICINES_NOTIFICATION.insert_one(notification_data)
        print(f"   ✓ Created notification at {notif_time.strftime('%H:%M')}")
    
    # 6. Create mock appointments
    print("\n6. Creating mock appointments...")
    
    # Delete old appointments for this user
    delete_result = await db.APPOINTMENTS.delete_many({"user_id": mock_user_id})
    print(f"   ✓ Deleted {delete_result.deleted_count} old appointments")
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    next_week = datetime.utcnow() + timedelta(days=7)
    
    appointment_dates = [
        tomorrow.replace(hour=10, minute=0, second=0, microsecond=0),
        next_week.replace(hour=14, minute=30, second=0, microsecond=0)
    ]
    
    for i, appt_date in enumerate(appointment_dates):
        pet_id = pet_ids[i % len(pet_ids)]
        
        appointment_data = {
            "_id": ObjectId(),
            "user_id": mock_user_id,
            "pet_id": pet_id,
            "appointment_date": appt_date,
            "status": "pending",
            "note": f"Checkup for {pet_names[i % len(pet_names)]}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.APPOINTMENTS.insert_one(appointment_data)
        print(f"   ✓ Created appointment on {appt_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Close connection
    client.close()
    print("\n✅ Mock data seeding completed successfully!")
    print(f"\nYou can now login with token: {token}")
    print(f"User: TestUser1 (ID: {mock_user_id})")
    print(f"\nThe following data was created:")
    print(f"- JWT Token linked to TestUser1")
    print(f"- {len(pet_ids)} pets")
    print(f"- {len(notification_times)} medicine notifications (today)")
    print(f"- {len(appointment_dates)} appointments (upcoming)")

if __name__ == "__main__":
    asyncio.run(seed_mock_data())
