"""
Appointment Schemas - Pydantic models for appointment data validation
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId validation"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            try:
                ObjectId(v)
                return v
            except Exception:
                raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId")


class AppointmentBase(BaseModel):
    """Base schema for appointment data"""
    pet_id: str
    location: str
    appointment_date: datetime
    status: Literal["Upcoming", "Completed", "Canceled"] = "Upcoming"
    note: Optional[str] = None

    @field_validator('pet_id')
    @classmethod
    def validate_pet_id(cls, v):
        """Validate pet_id is a valid ObjectId"""
        try:
            ObjectId(v)
            return v
        except Exception:
            raise ValueError("Invalid pet_id format")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pet_id": "507f1f77bcf86cd799439011",
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
    id: str = Field(alias="_id")
    note: Optional[str]
    pet_id: str
    appointment_date: datetime
    status: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "note": "Annual checkup",
                "pet_id": "507f1f77bcf86cd799439012",
                "appointment_date": "2026-01-20T14:00:00",
                "status": "Upcoming"
            }
        }
    )


class AppointmentDetail(BaseModel):
    """Full schema for appointment details"""
    id: str = Field(alias="_id")
    pet_id: str
    user_id: str
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
                "_id": "507f1f77bcf86cd799439011",
                "pet_id": "507f1f77bcf86cd799439012",
                "user_id": "507f1f77bcf86cd799439013",
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
