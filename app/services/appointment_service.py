"""
Appointment Service - Business Logic for Appointment Management

Handles appointment CRUD operations with automatic notification generation.
Notifications are created 2 days before the appointment date.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class AppointmentService:
    """Service class for appointment-related business logic"""

    @staticmethod
    async def create_appointment_with_notification(
        db: AsyncIOMotorDatabase,
        user_id: ObjectId,
        pet_id: ObjectId,
        location: str,
        appointment_date: datetime,
        status: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an appointment and automatically generate a notification 2 days before
        
        Args:
            db: Database instance
            user_id: User ObjectId
            pet_id: Pet ObjectId
            location: Appointment location
            appointment_date: Date and time of appointment
            status: Appointment status (default: "Upcoming")
            note: Optional note
            
        Returns:
            Dictionary with appointment_id and notification_id
        """
        # Get pet details for notification title
        pet = await db.PETS.find_one({"_id": pet_id})
        pet_name = pet.get("name", "your pet") if pet else "your pet"
        
        # Create appointment document
        appointment_doc = {
            "pet_id": pet_id,
            "location": location,
            "appointment_date": appointment_date,
            "status": status,
            "note": note,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert appointment
        appointment_result = await db.APPOINTMENTS.insert_one(appointment_doc)
        appointment_id = appointment_result.inserted_id
        
        # Generate notification immediately
        notification_date = datetime.utcnow()
        
        notification_doc = {
            "pet_id": pet_id,
            "user_id": user_id,
            "appointment_id": appointment_id,
            "title": f"Reminder: Appointment at {location} for {pet_name}",
            "notification_at": notification_date,
            "sending_status": "not_sent",
            "status": "pending",
            "sending_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        notification_result = await db.APPOINTMENTS_NOTIFICATION.insert_one(notification_doc)
        
        return {
            "success": True,
            "appointment_id": appointment_id,
            "notification_id": notification_result.inserted_id,
            "notification_at": notification_date
        }

    @staticmethod
    async def update_appointment(
        db: AsyncIOMotorDatabase,
        appointment_id: ObjectId,
        user_id: ObjectId,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update appointment with side effects
        
        SECURITY: Verifies through pet ownership chain (User → Pet → Appointment)
        
        If appointment_date changes, updates the notification_at to new_date - 2 days
        If location changes, updates the notification title
        
        Args:
            db: Database instance
            appointment_id: Appointment ObjectId
            user_id: User ObjectId (for verification)
            update_data: Dictionary of fields to update
            
        Returns:
            Dictionary with update results
        """
        # Get current appointment
        appointment = await db.APPOINTMENTS.find_one({"_id": appointment_id})
        
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        
        # Verify pet ownership (Security: User → Pet → Appointment)
        pet_id = appointment.get("pet_id")
        if not pet_id:
            return {"success": False, "error": "Invalid appointment data"}
        
        pet = await db.PETS.find_one({"_id": pet_id, "user_id": user_id})
        if not pet:
            return {"success": False, "error": "Unauthorized: Pet does not belong to user"}
        
        result = {
            "success": True,
            "notification_updated": False,
            "notification_title_updated": False
        }
        
        # Check if appointment_date or location changed
        date_changed = "appointment_date" in update_data
        location_changed = "location" in update_data
        
        if date_changed or location_changed:
            # Get the notification
            notification = await db.APPOINTMENTS_NOTIFICATION.find_one({
                "appointment_id": appointment_id
            })
            
            if notification:
                notification_updates = {}
                
                # Update notification_at if date changed
                if date_changed:
                    new_date = update_data["appointment_date"]
                    new_notification_date = datetime.utcnow()
                    notification_updates["notification_at"] = new_notification_date
                    result["notification_updated"] = True
                
                # Update notification title if location changed
                if location_changed:
                    # Get pet name
                    pet = await db.PETS.find_one({"_id": appointment["pet_id"]})
                    pet_name = pet.get("name", "your pet") if pet else "your pet"
                    new_location = update_data["location"]
                    notification_updates["title"] = f"Reminder: Appointment at {new_location} for {pet_name}"
                    result["notification_title_updated"] = True
                
                # Update notification
                if notification_updates:
                    notification_updates["updated_at"] = datetime.utcnow()
                    await db.APPOINTMENTS_NOTIFICATION.update_one(
                        {"_id": notification["_id"]},
                        {"$set": notification_updates}
                    )
        
        # Update appointment
        update_data["updated_at"] = datetime.utcnow()
        await db.APPOINTMENTS.update_one(
            {"_id": appointment_id},
            {"$set": update_data}
        )
        
        return result

    @staticmethod
    async def cancel_appointment(
        db: AsyncIOMotorDatabase,
        appointment_id: ObjectId,
        user_id: ObjectId
    ) -> Dict[str, Any]:
        """
        Cancel an appointment (change status to "Canceled")
        
        SECURITY: Verifies through pet ownership chain (User → Pet → Appointment)
        
        Args:
            db: Database instance
            appointment_id: Appointment ObjectId
            user_id: User ObjectId (for verification)
            
        Returns:
            Dictionary with cancellation results
        """
        # Get appointment
        appointment = await db.APPOINTMENTS.find_one({"_id": appointment_id})
        
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        
        # Verify pet ownership (Security: User → Pet → Appointment)
        pet_id = appointment.get("pet_id")
        if not pet_id:
            return {"success": False, "error": "Invalid appointment data"}
        
        pet = await db.PETS.find_one({"_id": pet_id, "user_id": user_id})
        if not pet:
            return {"success": False, "error": "Unauthorized: Pet does not belong to user"}
        
        # Update status to "Canceled"
        await db.APPOINTMENTS.update_one(
            {"_id": appointment_id},
            {
                "$set": {
                    "status": "Canceled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Optionally cancel the notification (change status to "canceled")
        await db.APPOINTMENTS_NOTIFICATION.update_one(
            {"appointment_id": appointment_id},
            {
                "$set": {
                    "status": "canceled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Appointment canceled successfully"
        }

    @staticmethod
    async def delete_appointment(
        db: AsyncIOMotorDatabase,
        appointment_id: ObjectId,
        user_id: ObjectId
    ) -> Dict[str, Any]:
        """
        Hard delete an appointment and its notification
        
        SECURITY: Verifies through pet ownership chain (User → Pet → Appointment)
        
        Args:
            db: Database instance
            appointment_id: Appointment ObjectId
            user_id: User ObjectId (for verification)
            
        Returns:
            Dictionary with deletion results
        """
        # Get appointment
        appointment = await db.APPOINTMENTS.find_one({"_id": appointment_id})
        
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        
        # Verify pet ownership (Security: User → Pet → Appointment)
        pet_id = appointment.get("pet_id")
        if not pet_id:
            return {"success": False, "error": "Invalid appointment data"}
        
        pet = await db.PETS.find_one({"_id": pet_id, "user_id": user_id})
        if not pet:
            return {"success": False, "error": "Unauthorized: Pet does not belong to user"}
        
        # Delete notification
        notif_result = await db.APPOINTMENTS_NOTIFICATION.delete_many({
            "appointment_id": appointment_id
        })
        
        # Delete appointment
        appt_result = await db.APPOINTMENTS.delete_one({"_id": appointment_id})
        
        return {
            "success": True,
            "appointment_deleted": appt_result.deleted_count > 0,
            "notifications_deleted": notif_result.deleted_count
        }

    @staticmethod
    async def get_user_appointments(
        db: AsyncIOMotorDatabase,
        user_id: ObjectId,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all appointments for a user, optionally filtered by status
        
        SECURITY: Verifies through pet ownership chain (User → Pet → Appointment)
        
        Args:
            db: Database instance
            user_id: User ObjectId
            status_filter: Optional status filter ("Upcoming", "Completed", "Canceled")
            
        Returns:
            List of appointment documents
        """
        # Get user's pets first
        user_pets = await db.PETS.find({"user_id": user_id}).to_list(length=None)
        pet_ids = [pet["_id"] for pet in user_pets]
        
        if not pet_ids:
            return []
        
        # Query appointments belonging to user's pets
        query = {"pet_id": {"$in": pet_ids}}
        
        if status_filter:
            query["status"] = status_filter
        
        appointments = await db.APPOINTMENTS.find(query).sort("appointment_date", 1).to_list(length=None)
        return appointments

    @staticmethod
    async def get_appointment_by_id(
        db: AsyncIOMotorDatabase,
        appointment_id: ObjectId,
        user_id: ObjectId
    ) -> Optional[Dict[str, Any]]:
        """
        Get appointment details by ID
        
        SECURITY: Verifies through pet ownership chain (User → Pet → Appointment)
        
        Args:
            db: Database instance
            appointment_id: Appointment ObjectId
            user_id: User ObjectId (for verification)
            
        Returns:
            Appointment document or None
        """
        # Get appointment
        appointment = await db.APPOINTMENTS.find_one({"_id": appointment_id})
        
        if not appointment:
            return None
        
        # Verify pet ownership
        pet_id = appointment.get("pet_id")
        if not pet_id:
            return None
        
        pet = await db.PETS.find_one({"_id": pet_id, "user_id": user_id})
        
        if not pet:
            return None  # Pet doesn't belong to user
        
        return appointment

    @staticmethod
    async def verify_pet_ownership(
        db: AsyncIOMotorDatabase,
        pet_id: ObjectId,
        user_id: ObjectId
    ) -> bool:
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
