
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Get MongoDB URL from environment or use default
# Note: You might need to set this environment variable if it's not in .env
MONGODB_URL = "mongodb+srv://antthanchanok25488_db_user:QXp4FvEsIc05gPi9@vetnurse-cluster.jdub2rj.mongodb.net"
DB_NAME = "pet_medic_db"

async def main():
    print(f"Connecting to {MONGODB_URL}...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print("\n--- CHECKING USERS ---")
    users = await db.USERS.find().to_list(length=5)
    for user in users:
        print(f"User: {user['_id']} - {user.get('fname')} {user.get('lname')}")
        
    print("\n--- CHECKING MEDICINES ---")
    medicines = await db.MEDICINES.find().to_list(length=10)
    print(f"Total Medicines found: {len(medicines)}")
    for med in medicines:
        print(f"Med: {med['_id']}")
        print(f"  Name: {med['name']}")
        print(f"  User: {med.get('user_id', 'MISSING')}")
        print(f"  Pet: {med.get('pet_id', 'MISSING')}")
        print(f"  Start: {med.get('start_date', 'MISSING')}")
        print(f"  End: {med.get('end_date', 'MISSING')}")
        print(f"  Frequency: {med.get('frequency', 'MISSING')}")
        print(f"  Reminder Time: {med.get('reminder_time', 'MISSING')}")
        
    print("\n--- CHECKING NOTIFICATIONS (ALL) ---")
    count = await db.MEDICINES_NOTIFICATION.count_documents({})
    print(f"Total Notifications: {count}")
    
    notifications = await db.MEDICINES_NOTIFICATION.find().sort("notification_at", -1).to_list(length=20)
    for notif in notifications:
        print(f"Notif: {notif['_id']}")
        print(f"  Title: {notif['title']}")
        print(f"  Time: {notif['notification_at']} (UTC)")
        print(f"  User: {notif['user_id']}")
        print(f"  Pet: {notif['pet_id']}")
        print(f"  Medicine: {notif['medicine_id']}")
        
    print("\n--- CHECKING DATE QUERY ---")
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"Current UTC Time: {now}")
    print(f"Querying for >= {today_start}")
    
    today_notifs = await db.MEDICINES_NOTIFICATION.find({
        "notification_at": {"$gte": today_start}
    }).to_list(length=None)
    
    print(f"Found {len(today_notifs)} notifications for today/future")
    for notif in today_notifs:
         print(f"  - {notif['title']} at {notif['notification_at']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
