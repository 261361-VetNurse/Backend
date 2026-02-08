"""
Appointment Schemas - Pydantic models for appointment data validation
"""

from pydantic import BaseModel, ConfigDict
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


class AppointmentResponse(BaseModel):
    """Standard response wrapper for appointment data"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
