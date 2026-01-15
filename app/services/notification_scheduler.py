"""
Notification Scheduler - Daily job to generate future notifications

This service runs at midnight every day to generate notifications
for the next day for all active medicines.
"""

import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.services.medicine_service import MedicineService


class NotificationScheduler:
    """Scheduler for automatic notification generation"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.db = None
        
    def set_database(self, db: AsyncIOMotorDatabase):
        """Set database instance"""
        self.db = db
        
    async def generate_daily_notifications(self):
        """
        Daily job: Generate notifications for all active medicines
        
        This runs at midnight and generates notifications for the next 2 days
        for all medicines that:
        1. Have status "TAKE" (not "STOP")
        2. Have not yet ended (end_date >= today)
        3. Have started or will start soon (start_date <= today + 2 days)
        """
        if not self.db:
            print("⚠️ Database not set for scheduler")
            return
            
        try:
            print(f"🔄 [{datetime.utcnow()}] Starting daily notification generation...")
            
            # Get current time
            now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
            two_days_ahead = now + timedelta(days=2)
            
            # Find all active medicines within the relevant date range
            active_medicines = await self.db.MEDICINES.find({
                "status": "TAKE",
                "end_date": {"$gte": now},
                "start_date": {"$lte": two_days_ahead}
            }).to_list(length=None)
            
            total_generated = 0
            medicines_processed = 0
            
            for medicine in active_medicines:
                medicine_id = medicine["_id"]
                
                # Check if notifications already exist for the next 2 days
                # to avoid duplicates
                existing_count = await self.db.MEDICINES_NOTIFICATION.count_documents({
                    "medicine_id": medicine_id,
                    "notification_at": {
                        "$gte": now,
                        "$lt": two_days_ahead
                    }
                })
                
                # If notifications already exist for this period, skip
                if existing_count > 0:
                    continue
                
                # Get pet details for notification title
                pet = await self.db.PETS.find_one({"_id": medicine["pet_id"]})
                pet_name = pet.get("name", "Unknown Pet") if pet else "Unknown Pet"
                
                # Parse reminder_times
                reminder_times = []
                for rt in medicine.get("reminder_time", []):
                    if isinstance(rt, datetime):
                        reminder_times.append(rt.strftime("%H:%M"))
                    elif isinstance(rt, str):
                        reminder_times.append(rt)
                
                # Generate notifications for next 2 days
                count = await MedicineService.generate_notifications(
                    db=self.db,
                    medicine_id=medicine_id,
                    user_id=medicine["user_id"],
                    pet_id=medicine["pet_id"],
                    medicine_name=medicine["name"],
                    pet_name=pet_name,
                    start_date=medicine["start_date"],
                    end_date=medicine["end_date"],
                    frequency=medicine["frequency"],
                    reminder_times=reminder_times,
                    days_ahead=2
                )
                
                if count > 0:
                    total_generated += count
                    medicines_processed += 1
            
            print(f"✅ Generated {total_generated} notifications for {medicines_processed} medicines")
            
        except Exception as e:
            print(f"❌ Error in daily notification generation: {str(e)}")
    
    def start(self):
        """Start the scheduler"""
        if not self.db:
            print("⚠️ Cannot start scheduler: Database not set")
            return
            
        # Schedule job to run at midnight every day (00:00)
        self.scheduler.add_job(
            self.generate_daily_notifications,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_notification_generation',
            name='Generate daily notifications for medicines',
            replace_existing=True
        )
        
        self.scheduler.start()
        print("🚀 Notification scheduler started (runs at midnight daily)")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 Notification scheduler stopped")


# Global scheduler instance
notification_scheduler = NotificationScheduler()
