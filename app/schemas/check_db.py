import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

async def check_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['pet_medic_db']
    
    print("="*60)
    print("DATABASE INSPECTION")
    print("="*60)
    
    # Check total notifications
    total_notifs = await db.MEDICINES_NOTIFICATION.count_documents({})
    print(f"\n📊 Total Notifications: {total_notifs}")
    
    # Check medicines
    total_meds = await db.MEDICINES.count_documents({})
    print(f"💊 Total Medicines: {total_meds}")
    
    # Check today's notifications
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    today_notifs = await db.MEDICINES_NOTIFICATION.find({
        "notification_at": {
            "$gte": today_start,
            "$lt": today_end
        }
    }).to_list(length=None)
    
    print(f"\n🔔 Today's Notifications ({datetime.now().strftime('%Y-%m-%d')}): {len(today_notifs)}")
    
    if today_notifs:
        print("\nToday's Notifications Details:")
        for i, n in enumerate(today_notifs[:5], 1):
            print(f"  {i}. {n['title']}")
            print(f"     Time: {n['notification_at']}")
            print(f"     Pet ID: {n['pet_id']}")
            print(f"     User ID: {n['user_id']}")
    
    # Check all notifications (first 5)
    print("\n📋 All Notifications (first 5):")
    all_notifs = await db.MEDICINES_NOTIFICATION.find({}).limit(5).to_list(length=5)
    for i, n in enumerate(all_notifs, 1):
        print(f"  {i}. {n['title']}")
        print(f"     Time: {n['notification_at']}")
        print(f"     Pet ID: {n['pet_id']}")
    
    # Check pets
    print("\n🐾 Pets in DB:")
    pets = await db.PETS.find({}).to_list(length=None)
    for pet in pets:
        print(f"  - {pet['name']} (ID: {pet['_id']}, Owner: {pet['user_id']})")
    
    # Check users
    print("\n👤 Users in DB:")
    users = await db.USERS.find({}).to_list(length=None)
    for user in users:
        print(f"  - {user['fname']} {user['lname']} (ID: {user['_id']})")
    
    # Check JWT tokens
    print("\n🔑 JWT Tokens:")
    jwts = await db.JWT.find({}).to_list(length=None)
    for jwt in jwts:
        print(f"  - Token: {jwt['access_token']}")
        print(f"    User ID: {jwt['user_id']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_db())
