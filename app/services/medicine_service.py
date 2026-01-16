"""
Medicine Service - Business Logic for Medicine Management
"""

from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class MedicineService:
    """Service class for medicine-related business logic"""

    @staticmethod
    def parse_frequency(frequency: str) -> List[int]:
        """
        Parse frequency string to list of day numbers
        
        Args:
            frequency: '-1' (daily) or '0'-'6' (Monday-Sunday)
            
        Returns:
            List of day numbers (0=Monday, 6=Sunday)
            
        Examples:
            '-1' -> [0, 1, 2, 3, 4, 5, 6] (daily)
            '0' -> [0] (Monday only)
            '2' -> [2] (Wednesday only)
            '0,2,4' -> [0, 2, 4] (Mon, Wed, Fri)
        """
        frequency = frequency.strip()
        
        # Check for daily (-1)
        if frequency == '-1':
            return list(range(7))  # All days
        
        # Parse single day or comma-separated days
        try:
            if ',' in frequency:
                # Multiple days like "0,2,4"
                days = [int(day.strip()) for day in frequency.split(',')]
            else:
                # Single day like "0" or "3"
                days = [int(frequency)]
            
            # Filter valid days (0-6)
            return [d for d in days if 0 <= d <= 6]
        except (ValueError, AttributeError):
            # Default to Monday if parsing fails
            return [0]

    @staticmethod
    def parse_time_string(time_str: str) -> time:
        """
        Parse time string in HH:MM format to time object
        
        Args:
            time_str: Time string in 'HH:MM' format, e.g., '08:00', '18:30'
            
        Returns:
            time object
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour=hour, minute=minute)
        except (ValueError, AttributeError):
            return time(hour=8, minute=0)  # Default to 8:00 AM

    @staticmethod
    async def generate_notifications(
        db: AsyncIOMotorDatabase,
        medicine_id: ObjectId,
        user_id: ObjectId,
        pet_id: ObjectId,
        medicine_name: str,
        pet_name: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str,
        reminder_times: List[str],
        days_ahead: int = 2
    ) -> int:
        """
        Generate notification records for a medicine (only for next N days)
        
        This generates notifications for a limited window (default 2 days ahead).
        A scheduled job should run daily to generate notifications for the next day.
        
        Args:
            db: Database instance
            medicine_id: Medicine ObjectId
            user_id: User ObjectId
            pet_id: Pet ObjectId
            medicine_name: Name of the medicine
            pet_name: Name of the pet
            start_date: Start date of medication
            end_date: End date of medication
            frequency: Frequency string ('daily', 'weekly', or day numbers)
            reminder_times: List of time strings in 'HH:MM' format
            days_ahead: Number of days to generate ahead (default: 2)
            
        Returns:
            Number of notifications created
        """
        # Parse frequency to get list of day numbers
        frequency_days = MedicineService.parse_frequency(frequency)
        
        # Calculate generation window
        now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        generation_end = now + timedelta(days=days_ahead)
        
        # Determine actual start date (max of start_date and now)
        actual_start = max(
            start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None),
            now
        )
        
        # Determine actual end date (min of end_date, generation_end)
        end_date_normalized = end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=None)
        actual_end = min(generation_end, end_date_normalized)
        
        # Skip if medicine period hasn't started yet or already ended
        if actual_start > actual_end:
            return 0
        
        current_date = actual_start
        notifications = []
        
        # Loop through each day in the generation window
        while current_date <= actual_end:
            # Check if current day matches frequency (0=Monday, 6=Sunday)
            weekday = current_date.weekday()
            
            if weekday in frequency_days:
                # Create notification for each reminder time
                for time_str in reminder_times:
                    reminder_time = MedicineService.parse_time_string(time_str)
                    
                    # Combine date and time (ensure no timezone info)
                    notification_datetime = datetime.combine(
                        current_date.date(),
                        reminder_time
                    ).replace(tzinfo=None)
                    
                    # Create notification title
                    title = f"Time to give {medicine_name} to {pet_name}"
                    
                    # Build notification document
                    notification_doc = {
                        "pet_id": pet_id,
                        "user_id": user_id,
                        "medicine_id": medicine_id,
                        "title": title,
                        "notification_at": notification_datetime,
                        "sending_status": "not_sent",
                        "status": "pending",
                        "sending_count": 0,
                        "istaken": False,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    notifications.append(notification_doc)
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Batch insert all notifications
        if notifications:
            result = await db.MEDICINES_NOTIFICATION.insert_many(notifications)
            return len(result.inserted_ids)
        
        return 0

    @staticmethod
    async def delete_future_notifications(
        db: AsyncIOMotorDatabase,
        medicine_id: ObjectId,
        only_not_taken: bool = True
    ) -> int:
        """
        Delete future notifications for a medicine
        
        Args:
            db: Database instance
            medicine_id: Medicine ObjectId
            only_not_taken: If True, only delete notifications where istaken=False
            
        Returns:
            Number of notifications deleted
        """
        current_time = datetime.utcnow().replace(tzinfo=None)
        
        query = {
            "medicine_id": medicine_id,
            "notification_at": {"$gte": current_time}
        }
        
        if only_not_taken:
            query["istaken"] = False
        
        result = await db.MEDICINES_NOTIFICATION.delete_many(query)
        return result.deleted_count

    @staticmethod
    async def update_medicine(
        db: AsyncIOMotorDatabase,
        medicine_id: ObjectId,
        user_id: ObjectId,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update medicine with complex side effects
        
        Handles two scenarios:
        - Scenario A: Schedule changes (frequency, dates, times) -> Regenerate notifications
        - Scenario B: Status changes to "stopped" -> Add note and delete future notifications
        
        Args:
            db: Database instance
            medicine_id: Medicine ObjectId
            user_id: User ObjectId
            update_data: Dictionary of fields to update
            
        Returns:
            Dictionary with update results
        """
        # Get current medicine data
        medicine = await db.MEDICINES.find_one({"_id": medicine_id, "user_id": user_id})
        if not medicine:
            return {"success": False, "error": "Medicine not found"}
        
        # Check for Scenario B: Status change to "STOP"
        status_changed_to_stopped = (
            "status" in update_data and 
            update_data["status"] == "STOP" and 
            medicine.get("status", "") != "STOP"
        )
        
        # Check for Scenario A: Schedule change
        schedule_fields = ["frequency", "start_date", "end_date", "reminder_time"]
        schedule_changed = any(field in update_data for field in schedule_fields)
        
        result = {
            "success": True,
            "notifications_deleted": 0,
            "notifications_created": 0,
            "note_added": False
        }
        
        # Scenario B: Status changed to "STOP"
        if status_changed_to_stopped:
            # Handle note addition (max 3 notes)
            if "note" in update_data and update_data["note"]:
                new_note = update_data["note"]
                # Use $push with $slice to keep only last 3 notes
                await db.MEDICINES.update_one(
                    {"_id": medicine_id},
                    {
                        "$push": {
                            "notes": {
                                "$each": [new_note],
                                "$slice": -3  # Keep last 3 notes
                            }
                        }
                    }
                )
                result["note_added"] = True
                # Remove 'note' from update_data as it's already handled
                del update_data["note"]
            
            # Delete all future notifications
            deleted_count = await MedicineService.delete_future_notifications(
                db, medicine_id, only_not_taken=False
            )
            result["notifications_deleted"] = deleted_count
        
        # Scenario A: Schedule changed
        elif schedule_changed:
            # Delete future untaken notifications
            deleted_count = await MedicineService.delete_future_notifications(
                db, medicine_id, only_not_taken=True
            )
            result["notifications_deleted"] = deleted_count
            
            # Get pet details for notification generation
            pet = await db.PETS.find_one({"_id": medicine["pet_id"]})
            pet_name = pet.get("name", "Unknown Pet") if pet else "Unknown Pet"
            
            # Prepare data for regeneration
            medicine_name = update_data.get("name", medicine.get("name", "Medicine"))
            start_date = update_data.get("start_date", medicine.get("start_date"))
            end_date = update_data.get("end_date", medicine.get("end_date"))
            frequency = update_data.get("frequency", medicine.get("frequency"))
            reminder_time = update_data.get("reminder_time", medicine.get("reminder_time", []))
            
            # Ensure dates are timezone-naive
            if start_date and hasattr(start_date, 'tzinfo') and start_date.tzinfo:
                start_date = start_date.replace(tzinfo=None)
            if end_date and hasattr(end_date, 'tzinfo') and end_date.tzinfo:
                end_date = end_date.replace(tzinfo=None)
            
            # Regenerate notifications with new schedule
            created_count = await MedicineService.generate_notifications(
                db=db,
                medicine_id=medicine_id,
                user_id=user_id,
                pet_id=medicine["pet_id"],
                medicine_name=medicine_name,
                pet_name=pet_name,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                reminder_times=reminder_time
            )
            result["notifications_created"] = created_count
        
        # Update medicine document (except 'note' which was handled separately)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await db.MEDICINES.update_one(
                {"_id": medicine_id},
                {"$set": update_data}
            )
        
        return result

    @staticmethod
    async def delete_medicine(
        db: AsyncIOMotorDatabase,
        medicine_id: ObjectId,
        user_id: ObjectId
    ) -> Dict[str, Any]:
        """
        Delete medicine and cascade delete all its notifications
        
        Args:
            db: Database instance
            medicine_id: Medicine ObjectId
            user_id: User ObjectId (for verification)
            
        Returns:
            Dictionary with deletion results
        """
        # Verify ownership through pet
        medicine = await db.MEDICINES.find_one({"_id": medicine_id})
        if not medicine:
            return {"success": False, "error": "Medicine not found"}
        
        # Verify pet belongs to user
        pet_id = medicine.get("pet_id")
        if not pet_id:
            return {"success": False, "error": "Medicine has no associated pet"}
        
        pet = await db.PETS.find_one({"_id": pet_id, "user_id": user_id})
        if not pet:
            return {"success": False, "error": "Access denied: Medicine belongs to a pet you don't own"}
        
        # Delete all notifications
        notif_result = await db.MEDICINES_NOTIFICATION.delete_many({"medicine_id": medicine_id})
        
        # Delete medicine
        med_result = await db.MEDICINES.delete_one({"_id": medicine_id})
        
        return {
            "success": True,
            "medicine_deleted": med_result.deleted_count > 0,
            "notifications_deleted": notif_result.deleted_count
        }

    @staticmethod
    async def get_user_pet_ids(db: AsyncIOMotorDatabase, user_id: ObjectId) -> List[ObjectId]:
        """
        Get all pet IDs belonging to a user
        
        Args:
            db: Database instance
            user_id: User ObjectId
            
        Returns:
            List of pet ObjectIds
        """
        pets = await db.PETS.find({"user_id": user_id}).to_list(length=None)
        return [pet["_id"] for pet in pets]

    @staticmethod
    async def verify_pet_ownership(db: AsyncIOMotorDatabase, pet_id: ObjectId, user_id: ObjectId) -> bool:
        """
        Verify that a pet belongs to a specific user
        
        Args:
            db: Database instance
            pet_id: Pet ObjectId
            user_id: User ObjectId
            
        Returns:
            True if pet belongs to user, False otherwise
        """
        pet = await db.PETS.find_one({"_id": pet_id, "user_id": user_id})
        return pet is not None

    @staticmethod
    async def verify_notification_ownership(
        db: AsyncIOMotorDatabase,
        notification_id: ObjectId,
        user_id: ObjectId
    ) -> bool:
        """
        Verify that a notification belongs to a user (through pet ownership)
        
        Args:
            db: Database instance
            notification_id: Notification ObjectId
            user_id: User ObjectId
            
        Returns:
            True if notification belongs to user's pet, False otherwise
        """
        notification = await db.MEDICINES_NOTIFICATION.find_one({"_id": notification_id})
        if not notification:
            return False
        
        # Check if the user_id matches directly
        return notification.get("user_id") == user_id

    @staticmethod
    async def verify_notification_belongs_to_medicine(
        db: AsyncIOMotorDatabase,
        notification_id: ObjectId,
        medicine_id: ObjectId
    ) -> bool:
        """
        Verify that a notification belongs to a specific medicine
        
        Args:
            db: Database instance
            notification_id: Notification ObjectId
            medicine_id: Medicine ObjectId
            
        Returns:
            True if notification belongs to the medicine, False otherwise
        """
        notification = await db.MEDICINES_NOTIFICATION.find_one({
            "_id": notification_id,
            "medicine_id": medicine_id
        })
        return notification is not None

    @staticmethod
    async def verify_medicine_ownership(
        db: AsyncIOMotorDatabase,
        medicine_id: ObjectId,
        user_id: ObjectId
    ) -> bool:
        """
        Verify that a medicine belongs to a user through pet ownership chain:
        Medicine → Pet → User
        
        Args:
            db: Database instance
            medicine_id: Medicine ObjectId
            user_id: User ObjectId
            
        Returns:
            True if medicine belongs to user's pet, False otherwise
        """
        # Get medicine
        medicine = await db.MEDICINES.find_one({"_id": medicine_id})
        if not medicine:
            return False
        
        # Get pet that owns this medicine
        pet_id = medicine.get("pet_id")
        if not pet_id:
            return False
        
        # Verify pet belongs to user
        pet = await db.PETS.find_one({
            "_id": pet_id,
            "user_id": user_id
        })
        return pet is not None

    @staticmethod
    async def verify_full_access_chain(
        db: AsyncIOMotorDatabase,
        notification_id: ObjectId,
        medicine_id: ObjectId,
        user_id: ObjectId
    ) -> dict:
        """
        Verify complete access chain: notification -> medicine -> user
        
        This ensures:
        1. Notification exists and belongs to user
        2. Medicine exists and belongs to user
        3. Notification is actually from this specific medicine
        
        Args:
            db: Database instance
            notification_id: Notification ObjectId
            medicine_id: Medicine ObjectId
            user_id: User ObjectId
            
        Returns:
            Dictionary with validation results and error message if any
        """
        # Check notification exists and belongs to user
        notification = await db.MEDICINES_NOTIFICATION.find_one({"_id": notification_id})
        if not notification:
            return {"valid": False, "error": "Notification not found"}
        
        if notification.get("user_id") != user_id:
            return {"valid": False, "error": "Notification does not belong to you"}
        
        # Check medicine exists
        medicine = await db.MEDICINES.find_one({"_id": medicine_id})
        if not medicine:
            return {"valid": False, "error": "Medicine not found"}
        
        # Check medicine belongs to user through pet ownership
        # Medicine → Pet → User
        pet_id = medicine.get("pet_id")
        if not pet_id:
            return {"valid": False, "error": "Medicine has no associated pet"}
        
        pet = await db.PETS.find_one({"_id": pet_id})
        if not pet:
            return {"valid": False, "error": "Pet not found"}
        
        if pet.get("user_id") != user_id:
            return {"valid": False, "error": "Medicine belongs to a pet you don't own"}
        
        # Check notification is from this medicine
        if notification.get("medicine_id") != medicine_id:
            return {
                "valid": False,
                "error": "Notification does not belong to this medicine. Access denied."
            }
        
        # All checks passed
        return {
            "valid": True,
            "notification": notification,
            "medicine": medicine,
            "pet": pet
        }
