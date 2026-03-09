"""
Appointment Service (SQL Version)
Handles appointment CRUD operations with automatic notification generation
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models_sql.appointment_model import Appointment, AppointmentNotification
from app.models_sql.pet_model import Pet

# Thai timezone (UTC+7) — matches MySQL session timezone configured in the project.
TH_TZ = timezone(timedelta(hours=7))


def _now_th() -> datetime:
    """Current Thai time (UTC+7) as a naive datetime, matching the DB session timezone."""
    return datetime.now(TH_TZ).replace(tzinfo=None)


class AppointmentServiceSQL:
    """Service class for appointment-related business logic (SQL version)"""

    @staticmethod
    def _to_naive_th(dt: datetime) -> datetime:
        """Strip tzinfo only — no timezone conversion. Frontend sends Thai time directly."""
        return dt.replace(tzinfo=None)

    @staticmethod
    async def _sync_appointment_notifications(
        session: AsyncSession,
        appointment: Appointment,
        pet_name: str,
    ) -> int:
        """
        Delete all unsent future notifications for this appointment,
        then recreate two reminders:
          1. 1 day before appointment_date  (หรือ now+15min ถ้าใกล้เกิน)
          2. At the exact appointment_date  (เตือนความจำตอนถึงเวลานัดจริง)
        Returns number of notifications created.
        """
        now = _now_th()

        # Remove any unsent future rows so we can recreate cleanly.
        await session.execute(
            delete(AppointmentNotification)
            .where(and_(
                AppointmentNotification.appointment_id == appointment.appointment_id,
                AppointmentNotification.sending_status == 'not_sent',
                AppointmentNotification.notification_at >= now,
            ))
        )

        min_notify = now + timedelta(minutes=15)
        location = appointment.location
        appt_date = appointment.appointment_date

        # Notification 1: 1 วันก่อนนัด (floor: now+15min)
        day_before_at = max(appt_date - timedelta(days=1), min_notify)

        # Notification 2: เวลานัดจริง (floor: now+15min)
        on_day_at = max(appt_date, min_notify)

        to_add = []

        # สร้าง day_before เฉพาะเมื่อยังก่อน on_day (ไม่ duplicate)
        if day_before_at < on_day_at:
            to_add.append(AppointmentNotification(
                user_id=appointment.user_id,
                pet_id=appointment.pet_id,
                appointment_id=appointment.appointment_id,
                title=f"Reminder: Appointment at {location} for {pet_name} (tomorrow)",
                notification_at=day_before_at,
                sending_status='not_sent',
                status='pending',
                sending_count=0,
            ))

        to_add.append(AppointmentNotification(
            user_id=appointment.user_id,
            pet_id=appointment.pet_id,
            appointment_id=appointment.appointment_id,
            title=f"It's time! Appointment at {location} for {pet_name}",
            notification_at=on_day_at,
            sending_status='not_sent',
            status='pending',
            sending_count=0,
        ))

        session.add_all(to_add)
        return len(to_add)
    
    @staticmethod
    async def create_appointment_with_notification(
        session: AsyncSession,
        user_id: int,
        pet_id: int,
        location: str,
        appointment_date: datetime,
        status: str = "Upcoming",
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create appointment and auto-generate notification
        
        Args:
            session: Database session
            user_id: User ID (denormalized)
            pet_id: Pet ID
            location: Appointment location
            appointment_date: Appointment date/time
            status: Status (default: "Upcoming")
            note: Optional note
            
        Returns:
            Result dict with appointment_id and notification_id
        """
        # Get pet details
        result = await session.execute(
            select(Pet).where(Pet.pet_id == pet_id)
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            return {"success": False, "error": "Pet not found"}
        
        pet_name = pet.name or "your pet"
        
        # Normalize datetime to avoid aware/naive comparison errors.
        normalized_appointment_date = AppointmentServiceSQL._to_naive_th(appointment_date)

        try:
            # Create appointment and notification in one transaction.
            appointment = Appointment(
                user_id=user_id,
                pet_id=pet_id,
                location=location,
                appointment_date=normalized_appointment_date,
                status=status,
                note=note,
                is_deleted=False,
            )
            session.add(appointment)
            await session.flush()

            # Create 2 notifications: 1 day before + at exact appointment time
            notifications_created = await AppointmentServiceSQL._sync_appointment_notifications(
                session=session,
                appointment=appointment,
                pet_name=pet_name,
            )

            await session.commit()
            await session.refresh(appointment)
        except Exception as e:
            await session.rollback()
            return {"success": False, "error": f"Failed to create appointment notification: {str(e)}"}

        return {
            "success": True,
            "appointment_id": appointment.appointment_id,
            "notifications_created": notifications_created,
        }
    
    @staticmethod
    async def update_appointment(
        session: AsyncSession,
        appointment_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update appointment with side effects
        
        If appointment_date or location changes, update notification
        
        Args:
            session: Database session
            appointment_id: Appointment ID
            user_id: User ID (for verification)
            update_data: Fields to update
            
        Returns:
            Result dict
        """
        # Get appointment with pet
        result = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.pet))
            .where(Appointment.appointment_id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        
        # Verify ownership
        if appointment.user_id != user_id:
            return {"success": False, "error": "Unauthorized"}
        
        response = {
            "success": True,
            "notification_updated": False,
            "notifications_synced": 0,
            "notification_title_updated": False
        }
        
        # Check if date or location changed
        date_changed = "appointment_date" in update_data
        location_changed = "location" in update_data
        
        if date_changed:
            update_data["appointment_date"] = AppointmentServiceSQL._to_naive_th(update_data["appointment_date"])
        
        # Update appointment fields
        for key, value in update_data.items():
            setattr(appointment, key, value)

        if date_changed or location_changed:
            pet = appointment.pet
            pet_name = pet.name if pet else "your pet"
            synced_count = await AppointmentServiceSQL._sync_appointment_notifications(
                session=session,
                appointment=appointment,
                pet_name=pet_name,
            )
            response["notifications_synced"] = synced_count
            response["notification_updated"] = True
            if location_changed:
                response["notification_title_updated"] = True

        await session.commit()
        return response
    
    @staticmethod
    async def cancel_appointment(
        session: AsyncSession,
        appointment_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Cancel appointment (change status to "Canceled")
        
        Args:
            session: Database session
            appointment_id: Appointment ID
            user_id: User ID (for verification)
            
        Returns:
            Result dict
        """
        result = await session.execute(
            select(Appointment).where(Appointment.appointment_id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        
        if appointment.user_id != user_id:
            return {"success": False, "error": "Unauthorized"}
        
        # Update status
        appointment.status = 'Canceled'
        
        # Cancel notification
        await session.execute(
            update(AppointmentNotification)
            .where(AppointmentNotification.appointment_id == appointment_id)
            .values(status='canceled')
        )
        
        await session.commit()
        
        return {"success": True, "status": "Canceled"}
    
    @staticmethod
    async def delete_appointment(
        session: AsyncSession,
        appointment_id: int,
        user_id: int
    ) -> bool:
        """
        Soft delete appointment (CASCADE deletes notifications)
        
        Args:
            session: Database session
            appointment_id: Appointment ID
            user_id: User ID (for verification)
            
        Returns:
            True if successful
        """
        result = await session.execute(
            select(Appointment).where(Appointment.appointment_id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return False
        
        if appointment.user_id != user_id:
            return False
        
        appointment.is_deleted = True
        await session.commit()
        return True
    
    @staticmethod
    async def get_appointment_by_id(
        session: AsyncSession,
        appointment_id: int
    ) -> Optional[Appointment]:
        """Get appointment by ID"""
        result = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.pet))
            .where(and_(Appointment.appointment_id == appointment_id, Appointment.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_appointments_by_pet(
        session: AsyncSession,
        pet_id: int
    ) -> List[Appointment]:
        """Get all appointments for a pet"""
        result = await session.execute(
            select(Appointment)
            .where(and_(Appointment.pet_id == pet_id, Appointment.is_deleted == False))
            .order_by(Appointment.appointment_date.asc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_appointments_by_user(
        session: AsyncSession,
        user_id: int,
        status: Optional[str] = None
    ) -> List[Appointment]:
        """Get all appointments for user (optionally filtered by status)"""
        conditions = [
            Appointment.user_id == user_id,
            Appointment.is_deleted == False
        ]
        
        if status:
            conditions.append(Appointment.status == status)
        
        result = await session.execute(
            select(Appointment)
            .where(and_(*conditions))
            .order_by(Appointment.appointment_date.asc())
        )
        return result.scalars().all()
