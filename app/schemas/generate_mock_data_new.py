import asyncio
import os
from datetime import datetime, timedelta, time
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "pet_medic_db"

# --- Helper Functions ---
def get_dummy_date(time_str):
    """แปลงเวลา string (เช่น '08:00') เป็น datetime object (ใช้วันที่ dummy เพื่อเก็บเวลา)"""
    t = datetime.strptime(time_str, "%H:%M").time()
    return datetime.combine(datetime(2000, 1, 1), t)

def generate_notifications(pet_id, user_id, medicine_id, medicine_name, pet_name, start_date, end_date, frequency_days, reminder_times):
    """
    สร้าง Notification ล่วงหน้าตามช่วงเวลา
    frequency_days: list ของ int (0=Mon, ... 6=Sun)
    """
    notifications = []
    # Use UTC time to match API queries
    current_date = start_date.replace(tzinfo=None) if start_date.tzinfo else start_date
    
    # วนลูปตั้งแต่วันเริ่มจนถึงวันจบ
    while current_date <= end_date:
        # เช็คว่าวันปัจจุบันตรงกับ frequency ที่ตั้งไว้ไหม
        if current_date.weekday() in frequency_days:
            for reminder_dt in reminder_times:
                # สร้างเวลาแจ้งเตือน (รวมวันที่ loop + เวลาจาก reminder)
                remind_time = reminder_dt.time()
                notification_at = datetime.combine(current_date.date(), remind_time)
                
                notifications.append({
                    "pet_id": pet_id,
                    "user_id": user_id,
                    "medicine_id": medicine_id,
                    "title": f"ได้เวลากินยา {medicine_name} ของน้อง {pet_name} แล้ว",
                    "notification_at": notification_at,
                    "sending_status": "pending",
                    "status": "active",
                    "sending_count": 0,
                    "istaken": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
        
        current_date += timedelta(days=1)
    
    return notifications

async def create_mock_data():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print(f"🔌 Connected to {DB_NAME}...")

    # ==========================================
    # 🧹 STEP 0: CLEAR EXISTING DATA
    # ==========================================
    print("\n🧹 Clearing existing data in all collections...")
    collections_to_clear = [
        "USERS", "PETS", "MEDICINES", "MEDICINES_NOTIFICATION", 
        "JWT", "PETS_RECORDS", "APPOINTMENTS", "APPOINTMENTS_NOTIFICATION"
    ]
    
    for col_name in collections_to_clear:
        # ใช้ delete_many({}) เพื่อลบข้อมูลแต่ยังเก็บ Index และ Validator ไว้
        await db[col_name].delete_many({})
        print(f"   - Cleared collection: {col_name}")
    print("✓ All data cleared.\n")

    # ==========================================
    # 🏗️ STEP 1: CREATE USERS
    # ==========================================
    print("🏗️ Creating Users...")
    users_data = [
        {
            "_id": ObjectId(),
            "fname": "TestUser1",
            "lname": "HasMeds",
            "contact": {"phone": "0811111111", "line_id": "line_user1", "email": "user1@example.com"},
            "address": {"address_line1": "123 Home", "province": "Bangkok", "country": "Thailand"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "fname": "TestUser2",
            "lname": "NoMeds",
            "contact": {"phone": "0822222222", "line_id": "line_user2", "email": "user2@example.com"},
            "address": {"address_line1": "456 Condo", "province": "Chiang Mai", "country": "Thailand"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    result_users = await db["USERS"].insert_many(users_data)
    user1_id = result_users.inserted_ids[0]
    user2_id = result_users.inserted_ids[1]
    print(f"   - User 1 ID: {user1_id}")
    print(f"   - User 2 ID: {user2_id}")

    # ==========================================
    # 🔑 STEP 2: CREATE JWT (20 Years Expiry)
    # ==========================================
    print("🔑 Creating JWT Tokens (Expires in 20 years)...")
    expiry_date = datetime.utcnow() + timedelta(days=365 * 20)
    jwt_data = [
        {
            "access_token": "mock_token_user_1_long_live",
            "user_id": str(user1_id),
            "key_id": "mock_key_1",
            "token_type": "bearer",
            "expires_in": expiry_date,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "access_token": "mock_token_user_2_long_live",
            "user_id": str(user2_id),
            "key_id": "mock_key_2",
            "token_type": "bearer",
            "expires_in": expiry_date,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    await db["JWT"].insert_many(jwt_data)

    # ==========================================
    # 🐶 STEP 3: CREATE PETS (User 1: 2 Pets, User 2: 1 Pet)
    # ==========================================
    print("🐶 Creating Pets...")
    # --- Pets for User 1 ---
    pets_u1_data = [
        {
            "_id": ObjectId(),
            "user_id": user1_id,
            "name": "Lucky", # Pet 1
            "species": "Dog",
            "breed": "Golden Retriever",
            "color": "Gold",
            "gender": "Male",
            "birth_date": datetime(2020, 5, 20),
            "weight_kg": 25.5,
            "allergies": [],
            "infecund": True,
            "profile_image": "http://mock.img/lucky.jpg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": user1_id,
            "name": "Mochi", # Pet 2
            "species": "Cat",
            "breed": "Persian",
            "color": "White",
            "gender": "Female",
            "birth_date": datetime(2021, 8, 15),
            "weight_kg": 4.2,
            "allergies": ["Seafood"],
            "infecund": False,
            "profile_image": "http://mock.img/mochi.jpg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    result_pets_u1 = await db["PETS"].insert_many(pets_u1_data)
    pet1_id = result_pets_u1.inserted_ids[0]
    pet2_id = result_pets_u1.inserted_ids[1]

    # --- Pet for User 2 ---
    pets_u2_data = [
        {
            "_id": ObjectId(),
            "user_id": user2_id,
            "name": "Cooper",
            "species": "Dog",
            "breed": "Pug",
            "color": "Fawn",
            "gender": "Male",
            "birth_date": datetime(2022, 1, 10),
            "weight_kg": 8.0,
            "allergies": [],
            "infecund": False,
            "profile_image": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    await db["PETS"].insert_many(pets_u2_data)

    # ==========================================
    # 💊 STEP 4: CREATE MEDICINES & NOTIFICATIONS (Only User 1)
    # ==========================================
    print("💊 Creating Medicines & Notifications (User 1 only)...")
    medicines_data = []
    notifications_data = []

    # >>> Medicine 1: Amoxycillin for Lucky (Pet 1) <<<
    # กินทุกวัน (Daily) เวลา 08:00 และ 20:00 เป็นเวลา 7 วัน
    med1_id = ObjectId()
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=7) 
    reminder_times = [get_dummy_date("08:00"), get_dummy_date("20:00")]
    
    medicines_data.append({
        "_id": med1_id,
        "user_id": user1_id,
        "pet_id": pet1_id,
        "name": "Amoxycillin",
        "notes": ["Take after meal"],
        "properties": "Antibiotic",
        "image_urls": [],
        "dosage": "1 tablet",
        "frequency": "-1",  # -1 = Daily
        "status": "TAKE",
        "reminder_time": reminder_times,
        "start_date": start_date,
        "end_date": end_date,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    # Generate Notifications for Med 1
    # Frequency: [0,1,2,3,4,5,6] means Mon-Sun
    notis_med1 = generate_notifications(
        pet1_id, user1_id, med1_id, "Amoxycillin", "Lucky",
        start_date, end_date, [0,1,2,3,4,5,6], reminder_times
    )
    notifications_data.extend(notis_med1)

    # >>> Medicine 2: Vitamin Gel for Mochi (Pet 2) <<<
    # กิน จันทร์(0), พุธ(2), ศุกร์(4) เวลา 10:00 เป็นเวลา 30 วัน
    med2_id = ObjectId()
    start_date_m2 = datetime.utcnow()
    end_date_m2 = start_date_m2 + timedelta(days=30)
    reminder_times_m2 = [get_dummy_date("10:00")]
    
    medicines_data.append({
        "_id": med2_id,
        "user_id": user1_id,
        "pet_id": pet2_id,
        "name": "Vitamin Gel",
        "notes": [],
        "properties": "Supplement",
        "image_urls": [],
        "dosage": "1 pump",
        "frequency": "0,2,4",  # 0=Mon, 2=Wed, 4=Fri
        "status": "TAKE",
        "reminder_time": reminder_times_m2,
        "start_date": start_date_m2,
        "end_date": end_date_m2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    # Generate Notifications for Med 2
    notis_med2 = generate_notifications(
        pet2_id, user1_id, med2_id, "Vitamin Gel", "Mochi",
        start_date_m2, end_date_m2, [0, 2, 4], reminder_times_m2
    )
    notifications_data.extend(notis_med2)

    # Insert Medicines and Notifications
    if medicines_data:
        await db["MEDICINES"].insert_many(medicines_data)
    if notifications_data:
        await db["MEDICINES_NOTIFICATION"].insert_many(notifications_data)

    print(f"   - User 1: Created {len(medicines_data)} Medicines")
    print(f"   - User 1: Generated {len(notifications_data)} Notifications")
    print(f"   - User 2: No Medicines created (as requested)")

    # ==========================================
    # 📊 STEP 5: PRINT TEST DATA SUMMARY
    # ==========================================
    print("\n" + "="*60)
    print("📊 TEST DATA SUMMARY - USE THESE IDs IN POSTMAN")
    print("="*60)
    print(f"\n🔑 ACCESS TOKENS:")
    print(f"   User 1 (TestUser1): mock_token_user_1_long_live")
    print(f"   User 2 (TestUser2): mock_token_user_2_long_live")
    
    print(f"\n👤 USER IDs:")
    print(f"   User 1 ID: {user1_id}")
    print(f"   User 2 ID: {user2_id}")
    
    print(f"\n🐾 PET IDs:")
    print(f"   Pet 1 (Lucky - User1's Dog): {pet1_id}")
    print(f"   Pet 2 (Mochi - User1's Cat): {pet2_id}")
    
    print(f"\n💊 MEDICINE IDs:")
    print(f"   Medicine 1 (Amoxycillin for Lucky): {med1_id}")
    print(f"   Medicine 2 (Vitamin Gel for Mochi): {med2_id}")
    
    # Get and display a few notification IDs for testing
    print(f"\n🔔 SAMPLE NOTIFICATION IDs:")
    if len(notifications_data) > 0:
        print(f"   Notification 1: {notifications_data[0]['_id']}")
    if len(notifications_data) > 1:
        print(f"   Notification 2: {notifications_data[1]['_id']}")
    if len(notifications_data) > 2:
        print(f"   Notification 3: {notifications_data[2]['_id']}")
    
    print(f"\n📈 STATISTICS:")
    print(f"   Total Users: 2")
    print(f"   Total Pets: 3 (User1: 2, User2: 1)")
    print(f"   Total Medicines: {len(medicines_data)}")
    print(f"   Total Notifications: {len(notifications_data)}")
    
    print("\n" + "="*60)
    print("💡 POSTMAN TESTING TIPS:")
    print("="*60)
    print("1. Import POSTMAN_MEDICATIONS_TESTS.json into Postman")
    print("2. Update collection variables with above IDs")
    print("3. Start with 'GET All Medications' to see all data")
    print("4. Copy notification_id and medicine_id for other tests")
    print("5. Test error cases with User 2 (has no medicines)")
    print("="*60)
    
    print("\n🎉 Mockup Data Created Successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_mock_data())