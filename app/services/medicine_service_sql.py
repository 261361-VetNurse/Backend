"""
Medicine Service (SQL Version)
Business logic for medicine management and notification generation
"""
from datetime import datetime, timedelta, time as time_obj
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models_sql.medicine_model import Medicine, MedicineNotification
from app.models_sql.pet_model import Pet


class MedicineServiceSQL:
    """Service class for medicine-related business logic (SQL version)"""
    
    @staticmethod
    def parse_frequency(frequency: str) -> List[int]:
        """
        Parse frequency string to list of day numbers
        
        Args:
            frequency: '-1' (daily) or '0'-'6' (Monday-Sunday) or comma-separated  
            
        Returns:
            List of day numbers (0=Monday, 6=Sunday)
            
        Examples:
            '-1' -> [0, 1, 2, 3, 4, 5, 6] (daily)
            '0' -> [0] (Monday only)
            '0,2,4' -> [0, 2, 4] (Mon, Wed, Fri)
        """
        frequency = frequency.strip()
        
        # Check for daily (-1)
        if frequency == '-1':
            return list(range(7))  # All days
        
        # Parse single day or comma-separated days
        try:
            if ',' in frequency:
                days = [int(day.strip()) for day in frequency.split(',')]
            else:
                days = [int(frequency)]
            
            # Filter valid days (0-6)
            return [d for d in days if 0 <= d <= 6]
        except (ValueError, AttributeError):
            return [0]  # Default to Monday
    
    @staticmethod
    def parse_time_string(time_str: str) -> time_obj:
        """
        Parse time string in HH:MM format to time object
        
        Args:
            time_str: Time string in 'HH:MM' format, e.g., '08:00', '18:30'
            
        Returns:
            time object
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            return time_obj(hour=hour, minute=minute)
        except (ValueError, AttributeError):
            return time_obj(hour=8, minute=0)  # Default to 8:00 AM
    
    @staticmethod
    async def generate_notifications(
        session: AsyncSession,
        medicine_id: int,
        user_id: int,
        pet_id: int,
        medicine_name: str,
        pet_name: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str,
        reminder_times: List[str],
        days_ahead: int = 2
    ) -> int:
        """
        Generate notification records for a medicine (for next N days)
        
        Args:
            session: Database session
            medicine_id: Medicine ID
            user_id: User ID (denormalized)
            pet_id: Pet ID (denormalized)
            medicine_name: Name of medicine
            pet_name: Name of pet
            start_date: Start date of medication
            end_date: End date of medication
            frequency: Frequency string
            reminder_times: List of time strings ['08:00', '20:00']
            days_ahead: Days to generate ahead (default: 2)
            
        Returns:
            Number of notifications created
        """
        # Parse frequency
        frequency_days = MedicineServiceSQL.parse_frequency(frequency)
        
        # Calculate generation window
        now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        generation_end = now + timedelta(days=days_ahead)
        
        # Normalize start_date/end_date to datetime (may be date or datetime)
        if hasattr(start_date, 'hour'):
            start_dt = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_dt = datetime.combine(start_date, datetime.min.time())
        
        if hasattr(end_date, 'hour'):
            end_dt = end_date.replace(hour=23, minute=59, second=59)
        else:
            end_dt = datetime.combine(end_date, datetime.max.time().replace(microsecond=0))
        
        # Determine actual start/end
        actual_start = max(start_dt, now)
        actual_end = min(generation_end, end_dt)
        
        if actual_start > actual_end:
            return 0
        
        current_date = actual_start
        notifications = []
        
        # Loop through each day
        while current_date <= actual_end:
            weekday = current_date.weekday()
            
            if weekday in frequency_days:
                for time_str in reminder_times:
                    reminder_time = MedicineServiceSQL.parse_time_string(time_str)
                    
                    notification_datetime = datetime.combine(
                        current_date.date(),
                        reminder_time
                    )
                    
                    title = f"Time to give {medicine_name} to {pet_name}"
                    
                    notification = MedicineNotification(
                        user_id=user_id,
                        pet_id=pet_id,
                        medicine_id=medicine_id,
                        title=title,
                        notification_at=notification_datetime,
                        sending_status='not_sent',
                        status='pending',
                        sending_count=0,
                        istaken=False,
                    )
                    notifications.append(notification)
            
            current_date += timedelta(days=1)
        
        # Batch insert
        if notifications:
            session.add_all(notifications)
            await session.commit()
            return len(notifications)
        
        return 0
    
    @staticmethod
    async def delete_future_notifications(
        session: AsyncSession,
        medicine_id: int,
        only_not_taken: bool = True
    ) -> int:
        """
        Delete future notifications for a medicine
        
        Args:
            session: Database session
            medicine_id: Medicine ID
            only_not_taken: If True, only delete where istaken=False
            
        Returns:
            Number deleted
        """
        current_time = datetime.utcnow()
        
        conditions = [
            MedicineNotification.medicine_id == medicine_id,
            MedicineNotification.notification_at >= current_time
        ]
        
        if only_not_taken:
            conditions.append(MedicineNotification.istaken == False)
        
        result = await session.execute(
            delete(MedicineNotification).where(and_(*conditions))
        )
        await session.commit()
        return result.rowcount
    
    @staticmethod
    async def update_medicine_notes(
        session: AsyncSession,
        medicine_id: int,
        new_note: str
    ) -> bool:
        """
        Add note to medicine (keep only last 3)
        
        Args:
            session: Database session
            medicine_id: Medicine ID
            new_note: Note to add
            
        Returns:
            True if successful
        """
        # Get current medicine
        result = await session.execute(
            select(Medicine).where(Medicine.medicine_id == medicine_id)
        )
        medicine = result.scalar_one_or_none()
        
        if not medicine:
            return False
        
        # Get current notes
        notes = medicine.notes or []
        notes.append(new_note)
        
        # Keep last 3
        medicine.notes = notes[-3:]
        
        await session.commit()
        return True
    
    @staticmethod
    async def update_medicine(
        session: AsyncSession,
        medicine_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update medicine with complex side effects
        
        Handles:
        - Scenario A: Schedule changes -> Regenerate notifications
        - Scenario B: Status = "STOP" -> Add note + Delete notifications
        
        Args:
            session: Database session
            medicine_id: Medicine ID
            user_id: User ID
            update_data: Fields to update
            
        Returns:
            Result dict
        """
        # Get current medicine
        result = await session.execute(
            select(Medicine)
            .options(selectinload(Medicine.pet))
            .where(and_(Medicine.medicine_id == medicine_id, Medicine.user_id == user_id))
        )
        medicine = result.scalar_one_or_none()
        
        if not medicine:
            return {"success": False, "error": "Medicine not found"}
        
        # Check Scenario B: Status -> STOP
        status_changed_to_stopped = (
            "status" in update_data and
            update_data["status"] == "STOP" and
            medicine.status != "STOP"
        )
        
        # Check Scenario A: Schedule change
        schedule_fields = ["frequency", "start_date", "end_date", "reminder_time"]
        schedule_changed = any(field in update_data for field in schedule_fields)
        
        response = {
            "success": True,
            "notifications_deleted": 0,
            "notifications_created": 0,
            "note_added": False
        }
        
        # Scenario B: Stop medicine
        if status_changed_to_stopped:
            # Add note if provided
            if "note" in update_data and update_data["note"]:
                await MedicineServiceSQL.update_medicine_notes(
                    session, medicine_id, update_data["note"]
                )
                response["note_added"] = True
                del update_data["note"]
            
            # Delete all future notifications
            deleted = await MedicineServiceSQL.delete_future_notifications(
                session, medicine_id, only_not_taken=False
            )
            response["notifications_deleted"] = deleted
        
        # Scenario A: Schedule changed
        elif schedule_changed:
            # Delete future untaken notifications
            deleted = await MedicineServiceSQL.delete_future_notifications(
                session, medicine_id, only_not_taken=True
            )
            response["notifications_deleted"] = deleted
            
            # Get pet name
            pet = medicine.pet
            pet_name = pet.name if pet else "Unknown Pet"
            
            # Prepare data for regeneration
            medicine_name = update_data.get("name", medicine.name)
            start_date = update_data.get("start_date", medicine.start_date)
            end_date = update_data.get("end_date", medicine.end_date)
            frequency = update_data.get("frequency", medicine.frequency)
            reminder_time = update_data.get("reminder_time", medicine.reminder_time)
            
            # Regenerate notifications
            created = await MedicineServiceSQL.generate_notifications(
                session=session,
                medicine_id=medicine_id,
                user_id=user_id,
                pet_id=medicine.pet_id,
                medicine_name=medicine_name,
                pet_name=pet_name,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                reminder_times=reminder_time
            )
            response["notifications_created"] = created
        
        # Update medicine fields
        if update_data:
            for key, value in update_data.items():
                setattr(medicine, key, value)
            
            await session.commit()
        
        return response
    
    @staticmethod
    async def create_medicine(
        session: AsyncSession,
        pet_id: int,
        medicine_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = await session.execute(
            select(Pet).where(Pet.pet_id == pet_id)
        )
        pet = result.scalar_one_or_none()
        if not pet:
            return {"success": False, "error": "Pet not found"}

        instruction = medicine_data.get("properties", "")
        final_reminders = medicine_data.get("reminder_time")
        final_frequency = medicine_data.get("frequency") 


        if not final_reminders or len(final_reminders) == 0:
            final_reminders, analyzed_freq = MedicineServiceSQL.analyze_reminder_logic(instruction)
            
            if not final_frequency:
                final_frequency = analyzed_freq

        if not final_frequency:
            final_frequency = "1"

        medicine = Medicine(
            pet_id=pet_id,
            user_id=pet.user_id,
            name=medicine_data["name"],
            properties=instruction,
            dosage=medicine_data.get("dosage"),
            frequency=final_frequency, 
            status='TAKE',
            reminder_time=final_reminders, 
            start_date=medicine_data["start_date"],
            end_date=medicine_data["end_date"],
            notes=medicine_data.get("notes", []),
            image_urls=medicine_data.get("image_urls", []),
            is_deleted=False,
        )
        
        session.add(medicine)
        await session.commit()
        await session.refresh(medicine)
        
        created_count = await MedicineServiceSQL.generate_notifications(
            session=session,
            medicine_id=medicine.medicine_id,
            user_id=medicine.user_id,
            pet_id=pet_id,
            medicine_name=medicine.name,
            pet_name=pet.name,
            start_date=medicine.start_date,
            end_date=medicine.end_date,
            frequency=medicine.frequency,
            reminder_times=medicine.reminder_time
        )
        
        return {
            "success": True,
            "medicine_id": medicine.medicine_id,
            "notifications_created": created_count
        }
    
    @staticmethod
    async def get_medicine_by_id(session: AsyncSession, medicine_id: int) -> Optional[Medicine]:
        """Get medicine by ID"""
        result = await session.execute(
            select(Medicine).where(Medicine.medicine_id == medicine_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_medicines_by_pet(session: AsyncSession, pet_id: int) -> List[Medicine]:
        """Get all medicines for a pet"""
        result = await session.execute(
            select(Medicine)
            .where(and_(Medicine.pet_id == pet_id, Medicine.is_deleted == False))
            .order_by(Medicine.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_medicine(session: AsyncSession, medicine_id: int) -> bool:
        """Soft delete medicine (CASCADE will delete notifications)"""
        result = await session.execute(
            update(Medicine)
            .where(Medicine.medicine_id == medicine_id)
            .values(is_deleted=True)
        )
        await session.commit()
        return result.rowcount > 0
    
    @staticmethod
    def analyze_reminder_logic(instruction: str):
        text = instruction or ""
        reminder_times = []
        
        if "เช้า" in text: reminder_times.append("07:00")
        if "กลางวัน" in text: reminder_times.append("12:00")
        if "เย็น" in text: reminder_times.append("18:00")
        if "ก่อนนอน" in text: reminder_times.append("21:00")

        # Logic: ถ้ากินวันละครั้ง/ทุกวัน แต่ไม่ระบุช่วงเวลา -> Default 07:00
        if not reminder_times:
            reminder_times = ["07:00"]
            
        if "ทุกวัน" in text :
            frequency = "-1"
        else:
            frequency = "1" 
            
        return reminder_times, frequency
