"""
Notification Scheduler (SQL Version)
Daily job to generate future notifications for medicines
"""
import asyncio
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_sql.base import AsyncSessionLocal
from app.models_sql.medicine_model import Medicine, MedicineNotification
from app.models_sql.pet_model import Pet
from app.services.medicine_service_sql import MedicineServiceSQL


class NotificationSchedulerSQL:
    """Scheduler for automatic notification generation (SQL version)"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.session_factory = AsyncSessionLocal
        
    async def generate_daily_notifications(self):
        """
        Daily job: Generate notifications for all active medicines
        Runs at midnight and generates notifications for the next 1 week (7 days)
        """
        async with self.session_factory() as session:
            try:
                now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                print(f"[{now}] Starting daily notification generation (SQL)...")
                one_week_ahead = now + timedelta(days=7)
                
                # Find all active medicines within the relevant date range
                result = await session.execute(
                    select(Medicine)
                    .where(and_(
                        Medicine.status == 'TAKE',
                        Medicine.end_date >= now.date(),
                        Medicine.start_date <= one_week_ahead.date(),
                        Medicine.is_deleted == False
                    ))
                )
                active_medicines = result.scalars().all()
                
                total_generated = 0
                medicines_processed = 0
                
                for medicine in active_medicines:
                    # Check if notifications already exist for this period
                    existing_result = await session.execute(
                        select(MedicineNotification)
                        .where(and_(
                            MedicineNotification.medicine_id == medicine.medicine_id,
                            MedicineNotification.notification_at >= now,
                            MedicineNotification.notification_at < one_week_ahead
                        ))
                    )
                    existing_notifications = existing_result.scalars().all()
                    
                    # Skip if notifications already exist
                    if len(existing_notifications) > 0:
                        continue
                    
                    # Get pet details
                    pet_result = await session.execute(
                        select(Pet).where(Pet.pet_id == medicine.pet_id)
                    )
                    pet = pet_result.scalar_one_or_none()
                    pet_name = pet.name if pet else "Unknown Pet"
                    
                    # Generate notifications
                    count = await MedicineServiceSQL.generate_notifications(
                        session=session,
                        medicine_id=medicine.medicine_id,
                        user_id=medicine.user_id,
                        pet_id=medicine.pet_id,
                        medicine_name=medicine.name,
                        pet_name=pet_name,
                        start_date=datetime.combine(medicine.start_date, datetime.min.time()),
                        end_date=datetime.combine(medicine.end_date, datetime.max.time()),
                        frequency=medicine.frequency,
                        reminder_times=medicine.reminder_time,
                        days_ahead=7
                    )
                    
                    if count > 0:
                        total_generated += count
                        medicines_processed += 1
                
                print(f"Generated {total_generated} notifications for {medicines_processed} medicines (SQL)")
                
            except Exception as e:
                print(f"Error in daily notification generation (SQL): {str(e)}")
                await session.rollback()
    
    def start(self):
        """Start the scheduler"""
        # Schedule job to run at midnight every day (00:00)
        self.scheduler.add_job(
            self.generate_daily_notifications,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_notification_generation_sql',
            name='Generate daily notifications for medicines (SQL)',
            replace_existing=True
        )
        
        self.scheduler.start()
        print("Notification scheduler started (SQL version - runs at midnight daily)")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Notification scheduler stopped (SQL)")


# Global scheduler instance (SQL version)
notification_scheduler_sql = NotificationSchedulerSQL()
