"""
Notification Schemas - Pydantic V2 Models
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class NotificationFeedItem(BaseModel):
    """Lightweight schema for notification list/feed view"""
    id: int = Field(..., alias="_id", description="Notification ID")
    title: str = Field(..., description="Notification title")
    notification_at: datetime = Field(..., description="Scheduled notification time")
    istaken: bool = Field(..., description="Whether medicine was taken")
    pet_id: int = Field(..., description="Pet ID")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class NotificationDetail(BaseModel):
    """Full schema for notification detail view"""
    id: int = Field(..., alias="_id", description="Notification ID")
    pet_id: int = Field(..., description="Pet ID")
    user_id: int = Field(..., description="User ID")
    medicine_id: int = Field(..., description="Medicine ID")
    title: str = Field(..., description="Notification title")
    notification_at: datetime = Field(..., description="Scheduled notification time")
    sending_status: str = Field(..., description="Sending status: not_sent, sent, failed")
    status: str = Field(..., description="Status: pending, sent, failed")
    sending_count: int = Field(..., description="Number of times notification was sent")
    istaken: bool = Field(..., description="Whether medicine was taken")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class MarkTakenRequest(BaseModel):
    """Schema for marking medicine as taken"""
    istaken: Optional[bool] = Field(default=True, description="Mark as taken or not taken")

