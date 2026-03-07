"""
Notification Scheduler (SQL Version)
Daily job to generate future notifications for medicines
"""
import asyncio
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_sql.base import AsyncSessionLocal
from app.models_sql.medicine_model import Medicine, MedicineNotification
from app.models_sql.appointment_model import AppointmentNotification
from app.models_sql.pet_model import Pet
from app.models_sql.user_model import User
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
    
    async def send_pending_notifications(self):
        """
        Runs every 5 minutes: dispatch LINE push for medicine and appointment
        notifications due within the next 15 minutes that have not been sent yet.
        Updates sending_status='sent', status='sent', sending_count+1 on success,
        or sending_status='failed', status='failed', sending_count+1 on error.
        """
        from app.services.line_service import send_push_notification

        async with self.session_factory() as session:
            try:
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                window_end = now + timedelta(minutes=15)

                # --- Medicine Notifications ---
                med_result = await session.execute(
                    select(MedicineNotification, User)
                    .join(User, MedicineNotification.user_id == User.user_id)
                    .where(and_(
                        MedicineNotification.sending_status == 'not_sent',
                        MedicineNotification.status == 'pending',
                        MedicineNotification.notification_at <= window_end,
                    ))
                )
                med_rows = med_result.all()

                med_sent = 0
                for notif, user in med_rows:
                    try:
                        date_str = notif.notification_at.strftime("%Y-%m-%d %H:%M")
                        await send_push_notification(user.line_id, notif.title, date_str)
                        notif.sending_status = 'sent'
                        notif.status = 'sent'
                        notif.sending_count = (notif.sending_count or 0) + 1
                        med_sent += 1
                    except Exception as e:
                        print(f"[Sender] Failed medicine notification {notif.notification_id}: {e}")
                        notif.sending_status = 'failed'
                        notif.status = 'failed'
                        notif.sending_count = (notif.sending_count or 0) + 1

                # --- Appointment Notifications ---
                appt_result = await session.execute(
                    select(AppointmentNotification, User)
                    .join(User, AppointmentNotification.user_id == User.user_id)
                    .where(and_(
                        AppointmentNotification.sending_status == 'not_sent',
                        AppointmentNotification.status == 'pending',
                        AppointmentNotification.notification_at <= window_end,
                    ))
                )
                appt_rows = appt_result.all()

                appt_sent = 0
                for notif, user in appt_rows:
                    try:
                        date_str = notif.notification_at.strftime("%Y-%m-%d %H:%M")
                        await send_push_notification(user.line_id, notif.title, date_str)
                        notif.sending_status = 'sent'
                        notif.status = 'sent'
                        notif.sending_count = (notif.sending_count or 0) + 1
                        appt_sent += 1
                    except Exception as e:
                        print(f"[Sender] Failed appointment notification {notif.notification_id}: {e}")
                        notif.sending_status = 'failed'
                        notif.status = 'failed'
                        notif.sending_count = (notif.sending_count or 0) + 1

                if med_rows or appt_rows:
                    await session.commit()

                if med_sent > 0 or appt_sent > 0:
                    print(f"[Sender] Dispatched {med_sent} medicine + {appt_sent} appointment notifications")

            except Exception as e:
                print(f"[Sender] Error in notification dispatch: {str(e)}")
                await session.rollback()

    def start(self):
        """Start the scheduler"""
        # Job 1: Generate notification rows daily at midnight
        self.scheduler.add_job(
            self.generate_daily_notifications,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_notification_generation_sql',
            name='Generate daily notifications for medicines (SQL)',
            replace_existing=True
        )

        # Job 2: Dispatch LINE push every 5 minutes for notifications due within 15 min
        self.scheduler.add_job(
            self.send_pending_notifications,
            trigger=IntervalTrigger(minutes=5),
            id='notification_dispatcher',
            name='Send pending LINE push notifications',
            replace_existing=True,
        )

        self.scheduler.start()
        print("Notification scheduler started (SQL version: midnight generator + 5-min dispatcher)")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Notification scheduler stopped (SQL)")


# Global scheduler instance (SQL version)
notification_scheduler_sql = NotificationSchedulerSQL()
