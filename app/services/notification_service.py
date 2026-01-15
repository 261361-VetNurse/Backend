"""
Notification Service - Business Logic for Notification Management
"""

from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class NotificationService:
    """Service class for notification-related business logic"""

    @staticmethod
    async def get_notifications_by_date(
        db: AsyncIOMotorDatabase,
        pet_ids: List[ObjectId],
        target_date: datetime
    ) -> List[dict]:
        """
        Get all notifications for specific pets on a specific date
        
        Args:
            db: Database instance
            pet_ids: List of pet ObjectIds
            target_date: Target date to filter notifications
            
        Returns:
            List of notification documents
        """
        # Set date range for filtering (entire day)
        date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        # Build query
        query = {
            "pet_id": {"$in": pet_ids},
            "notification_at": {
                "$gte": date_start,
                "$lt": date_end
            }
        }
        
        # Fetch notifications sorted by time
        notifications = await db.MEDICINES_NOTIFICATION.find(query).sort(
            "notification_at", 1
        ).to_list(length=None)
        
        return notifications

    @staticmethod
    async def get_notification_by_id(
        db: AsyncIOMotorDatabase,
        notification_id: ObjectId
    ) -> Optional[dict]:
        """
        Get a single notification by ID
        
        Args:
            db: Database instance
            notification_id: Notification ObjectId
            
        Returns:
            Notification document or None
        """
        return await db.MEDICINES_NOTIFICATION.find_one({"_id": notification_id})

    @staticmethod
    async def mark_notification_taken(
        db: AsyncIOMotorDatabase,
        notification_id: ObjectId,
        istaken: bool = True
    ) -> bool:
        """
        Mark a notification as taken or not taken
        
        Args:
            db: Database instance
            notification_id: Notification ObjectId
            istaken: Whether medicine was taken
            
        Returns:
            True if update successful, False otherwise
        """
        result = await db.MEDICINES_NOTIFICATION.update_one(
            {"_id": notification_id},
            {
                "$set": {
                    "istaken": istaken,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0

    @staticmethod
    async def verify_notification_belongs_to_user(
        db: AsyncIOMotorDatabase,
        notification_id: ObjectId,
        user_id: ObjectId
    ) -> bool:
        """
        Verify that a notification belongs to a user
        
        Args:
            db: Database instance
            notification_id: Notification ObjectId
            user_id: User ObjectId
            
        Returns:
            True if notification belongs to user, False otherwise
        """
        notification = await db.MEDICINES_NOTIFICATION.find_one({
            "_id": notification_id,
            "user_id": user_id
        })
        
        return notification is not None
