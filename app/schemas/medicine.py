"""
Medicine Schemas - Pydantic V2 Models
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


class MedicineBase(BaseModel):
    """Base schema for Medicine"""
    name: str = Field(..., description="Medicine name")
    notes: Optional[List[str]] = Field(default=[], description="History notes (max 3)")
    properties: Optional[str] = Field(None, description="Medicine properties/description")
    image_urls: Optional[List[str]] = Field(default=[], description="Medicine image URLs")
    dosage: Optional[str] = Field(None, description="Dosage information, e.g., '1 tablet'")
    frequency: str = Field(..., description="Frequency: 'daily', 'weekly', or comma-separated day numbers (0=Mon, 6=Sun)")
    status: Optional[str] = Field(default="TAKE", description="Status: TAKE=active, STOP=stopped")
    reminder_time: List[str] = Field(..., description="List of times in HH:MM format, e.g., ['08:00', '18:00']")
    start_date: datetime = Field(..., description="Start date of medication")
    end_date: datetime = Field(..., description="End date of medication")


class MedicineCreate(MedicineBase):
    """Schema for creating a new Medicine"""
    pet_id: int = Field(..., description="Pet ID")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pet_id": 2,
                "name": "Amoxicillin",
                "dosage": "1 tablet",
                "frequency": "-1",
                "status": "TAKE",
                "reminder_time": ["08:00", "20:00"],
                "start_date": "2026-02-01T00:00:00",
                "end_date": "2026-02-28T00:00:00",
                "properties": "Antibiotic for infection",
                "image_urls": []
            }
        }
    )


class MedicineUpdate(BaseModel):
    """Schema for updating a Medicine (Partial updates allowed)"""
    name: Optional[str] = None
    notes: Optional[List[str]] = Field(None, description="Array of notes (replaces existing)")
    note: Optional[str] = Field(None, description="New note to add (used when status changes)")
    properties: Optional[str] = None
    image_urls: Optional[List[str]] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    status: Optional[str] = None
    reminder_time: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "STOP",
                "note": "Treatment completed successfully"
            }
        }
    )


class MedicineResponse(MedicineBase):
    """Schema for Medicine response"""
    id: int = Field(..., alias="_id", description="Medicine ID")
    user_id: int = Field(..., description="User ID")
    pet_id: int = Field(..., description="Pet ID")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

