"""
Appointment Service (SQL Version)
Handles appointment CRUD operations with automatic notification generation
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models_sql.appointment_model import Appointment, AppointmentNotification
from app.models_sql.pet_model import Pet


class AppointmentServiceSQL:
    """Service class for appointment-related business logic (SQL version)"""
    
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
        
        # Create appointment (user_id auto-populated by trigger)
        appointment = Appointment(
            user_id=user_id,  # Set explicitly
            pet_id=pet_id,
            location=location,
            appointment_date=appointment_date,
            status=status,
            note=note,
            is_deleted=False,
        )
        
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)
        
        # Create notification immediately
        notification_date = datetime.utcnow()
        
        notification = AppointmentNotification(
            user_id=user_id,
            pet_id=pet_id,
            appointment_id=appointment.appointment_id,
            title=f"Reminder: Appointment at {location} for {pet_name}",
            notification_at=notification_date,
            sending_status='not_sent',
            status='pending',
            sending_count=0,
        )
        
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        
        return {
            "success": True,
            "appointment_id": appointment.appointment_id,
            "notification_id": notification.notification_id,
            "notification_at": notification_date
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
            "notification_title_updated": False
        }
        
        # Check if date or location changed
        date_changed = "appointment_date" in update_data
        location_changed = "location" in update_data
        
        if date_changed or location_changed:
            # Get notification
            notif_result = await session.execute(
                select(AppointmentNotification)
                .where(AppointmentNotification.appointment_id == appointment_id)
            )
            notification = notif_result.scalar_one_or_none()
            
            if notification:
                # Update notification_at if date changed
                if date_changed:
                    notification.notification_at = datetime.utcnow()
                    response["notification_updated"] = True
                
                # Update title if location changed
                if location_changed:
                    pet = appointment.pet
                    pet_name = pet.name if pet else "your pet"
                    new_location = update_data["location"]
                    notification.title = f"Reminder: Appointment at {new_location} for {pet_name}"
                    response["notification_title_updated"] = True
                
                await session.commit()
        
        # Update appointment fields
        for key, value in update_data.items():
            setattr(appointment, key, value)
        
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
