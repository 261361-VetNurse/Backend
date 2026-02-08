"""
Appointment Schemas - Pydantic models for appointment data validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime


class AppointmentBase(BaseModel):
    """Base schema for appointment data"""
    pet_id: int
    location: str
    appointment_date: datetime
    status: Literal["Upcoming", "Completed", "Canceled"] = "Upcoming"
    note: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pet_id": 1,
                "location": "ABC Veterinary Clinic",
                "appointment_date": "2026-01-20T14:00:00",
                "status": "Upcoming",
                "note": "Annual checkup"
            }
        }
    )


class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment (all fields optional)"""
    location: Optional[str] = None
    appointment_date: Optional[datetime] = None
    status: Optional[Literal["Upcoming", "Completed", "Canceled"]] = None
    note: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "location": "XYZ Animal Hospital",
                "appointment_date": "2026-01-22T15:00:00",
                "status": "Upcoming",
                "note": "Updated: Bring vaccination records"
            }
        }
    )


class AppointmentFeedItem(BaseModel):
    """Lightweight schema for appointment list view"""
    id: int = Field(alias="_id")
    note: Optional[str]
    pet_id: int
    appointment_date: datetime
    status: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": 1,
                "note": "Annual checkup",
                "pet_id": 2,
                "appointment_date": "2026-01-20T14:00:00",
                "status": "Upcoming"
            }
        }
    )


class AppointmentDetail(BaseModel):
    """Full schema for appointment details"""
    id: int = Field(alias="_id")
    pet_id: int
    user_id: int
    location: str
    appointment_date: datetime
    status: str
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": 1,
                "pet_id": 2,
                "user_id": 3,
                "location": "ABC Veterinary Clinic",
                "appointment_date": "2026-01-20T14:00:00",
                "status": "Upcoming",
                "note": "Annual checkup",
                "created_at": "2026-01-15T10:00:00",
                "updated_at": "2026-01-15T10:00:00"
            }
        }
    )


class AppointmentResponse(BaseModel):
    """Standard response wrapper for appointment data"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
