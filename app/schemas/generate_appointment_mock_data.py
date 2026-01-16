"""
Generate Mock Data for Appointments Testing

This script creates test data for the Appointments module:
- Uses existing users and pets from previous mock data
- Creates appointments with notifications
"""

import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "pet_medic_db"


async def create_appointment_mock_data():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print(f"🔌 Connected to {DB_NAME}...")

    try:
        # ==========================================
        # Get Existing Users and Pets
        # ==========================================
        users = await db.USERS.find().limit(2).to_list(length=2)
        if len(users) < 2:
            print("❌ Error: Need at least 2 users. Run generate_mock_data_new.py first!")
            return
        
        user1_id = users[0]["_id"]
        user2_id = users[1]["_id"]
        
        print(f"✓ Found User 1: {users[0]['fname']} {users[0]['lname']} (ID: {user1_id})")
        print(f"✓ Found User 2: {users[1]['fname']} {users[1]['lname']} (ID: {user2_id})")
        
        # Get pets for each user
        pets_u1 = await db.PETS.find({"user_id": user1_id}).to_list(length=None)
        pets_u2 = await db.PETS.find({"user_id": user2_id}).to_list(length=None)
        
        if not pets_u1:
            print("❌ Error: User 1 has no pets!")
            return
        
        pet1_id = pets_u1[0]["_id"]
        pet1_name = pets_u1[0]["name"]
        print(f"✓ Found Pet 1: {pet1_name} (ID: {pet1_id})")
        
        if len(pets_u1) > 1:
            pet2_id = pets_u1[1]["_id"]
            pet2_name = pets_u1[1]["name"]
            print(f"✓ Found Pet 2: {pet2_name} (ID: {pet2_id})")
        
        if pets_u2:
            pet3_id = pets_u2[0]["_id"]
            pet3_name = pets_u2[0]["name"]
            print(f"✓ Found Pet 3: {pet3_name} (ID: {pet3_id})")

        # ==========================================
        # Clear Existing Appointments Data
        # ==========================================
        print("\n🧹 Clearing existing appointments data...")
        await db.APPOINTMENTS.delete_many({})
        await db.APPOINTMENTS_NOTIFICATION.delete_many({})
        print("✓ Cleared APPOINTMENTS and APPOINTMENTS_NOTIFICATION collections")

        # ==========================================
        # Create Appointments
        # ==========================================
        print("\n📅 Creating Appointments...")
        
        appointments_data = []
        notifications_data = []
        
        # Appointment 1: User 1, Pet 1 (Upcoming - 5 days from now)
        appt1_date = datetime.utcnow() + timedelta(days=5)
        appt1_id = ObjectId()
        
        appointments_data.append({
            "_id": appt1_id,
            "user_id": user1_id,
            "pet_id": pet1_id,
            "location": "ABC Veterinary Clinic",
            "appointment_date": appt1_date,
            "status": "Upcoming",
            "note": "Annual checkup and vaccination",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Notification 2 days before
        notifications_data.append({
            "pet_id": pet1_id,
            "user_id": user1_id,
            "appointment_id": appt1_id,
            "title": f"Reminder: Appointment at ABC Veterinary Clinic for {pet1_name}",
            "notification_at": appt1_date - timedelta(days=2),
            "sending_status": "not_sent",
            "status": "pending",
            "sending_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Appointment 2: User 1, Pet 2 (Upcoming - 10 days from now)
        if len(pets_u1) > 1:
            appt2_date = datetime.utcnow() + timedelta(days=10)
            appt2_id = ObjectId()
            
            appointments_data.append({
                "_id": appt2_id,
                "user_id": user1_id,
                "pet_id": pet2_id,
                "location": "XYZ Animal Hospital",
                "appointment_date": appt2_date,
                "status": "Upcoming",
                "note": "Dental cleaning",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            notifications_data.append({
                "pet_id": pet2_id,
                "user_id": user1_id,
                "appointment_id": appt2_id,
                "title": f"Reminder: Appointment at XYZ Animal Hospital for {pet2_name}",
                "notification_at": appt2_date - timedelta(days=2),
                "sending_status": "not_sent",
                "status": "pending",
                "sending_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Appointment 3: User 1, Pet 1 (Completed - 10 days ago)
        appt3_date = datetime.utcnow() - timedelta(days=10)
        appt3_id = ObjectId()
        
        appointments_data.append({
            "_id": appt3_id,
            "user_id": user1_id,
            "pet_id": pet1_id,
            "location": "ABC Veterinary Clinic",
            "appointment_date": appt3_date,
            "status": "Completed",
            "note": "Blood test results: All normal",
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(days=10)
        })
        
        # No notification for completed (already happened)
        
        # Appointment 4: User 2, Pet 3 (Upcoming - 7 days from now)
        if pets_u2:
            appt4_date = datetime.utcnow() + timedelta(days=7)
            appt4_id = ObjectId()
            
            appointments_data.append({
                "_id": appt4_id,
                "user_id": user2_id,
                "pet_id": pet3_id,
                "location": "Pet Care Center",
                "appointment_date": appt4_date,
                "status": "Upcoming",
                "note": "Grooming and nail trimming",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            notifications_data.append({
                "pet_id": pet3_id,
                "user_id": user2_id,
                "appointment_id": appt4_id,
                "title": f"Reminder: Appointment at Pet Care Center for {pet3_name}",
                "notification_at": appt4_date - timedelta(days=2),
                "sending_status": "not_sent",
                "status": "pending",
                "sending_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Appointment 5: User 1, Pet 1 (Canceled)
        appt5_date = datetime.utcnow() + timedelta(days=15)
        appt5_id = ObjectId()
        
        appointments_data.append({
            "_id": appt5_id,
            "user_id": user1_id,
            "pet_id": pet1_id,
            "location": "Emergency Vet",
            "appointment_date": appt5_date,
            "status": "Canceled",
            "note": "Owner canceled - pet recovered",
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow()
        })
        
        # Notification canceled
        notifications_data.append({
            "pet_id": pet1_id,
            "user_id": user1_id,
            "appointment_id": appt5_id,
            "title": f"Reminder: Appointment at Emergency Vet for {pet1_name}",
            "notification_at": appt5_date - timedelta(days=2),
            "sending_status": "not_sent",
            "status": "canceled",
            "sending_count": 0,
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow()
        })
        
        # Insert data
        if appointments_data:
            await db.APPOINTMENTS.insert_many(appointments_data)
            print(f"✓ Created {len(appointments_data)} appointments")
        
        if notifications_data:
            await db.APPOINTMENTS_NOTIFICATION.insert_many(notifications_data)
            print(f"✓ Created {len(notifications_data)} appointment notifications")
        
        # ==========================================
        # Summary
        # ==========================================
        print("\n" + "="*60)
        print("📊 MOCK DATA SUMMARY")
        print("="*60)
        print(f"Total Appointments: {len(appointments_data)}")
        print(f"Total Notifications: {len(notifications_data)}")
        print("\nAppointments by Status:")
        upcoming = sum(1 for a in appointments_data if a["status"] == "Upcoming")
        completed = sum(1 for a in appointments_data if a["status"] == "Completed")
        canceled = sum(1 for a in appointments_data if a["status"] == "Canceled")
        print(f"  - Upcoming: {upcoming}")
        print(f"  - Completed: {completed}")
        print(f"  - Canceled: {canceled}")
        print("\n" + "="*60)
        print("✅ Mock data generation completed successfully!")
        print("="*60)
        
        # Print some IDs for testing
        print("\n📋 TEST DATA IDs:")
        print(f"User 1 ID: {user1_id}")
        print(f"Pet 1 ID: {pet1_id}")
        if appointments_data:
            print(f"First Appointment ID: {appointments_data[0]['_id']}")
            print(f"First Notification ID: {notifications_data[0]['appointment_id']}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(create_appointment_mock_data())
