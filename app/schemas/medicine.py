"""
Medicine Schemas - Pydantic V2 Models
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId validation and serialization"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ],
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class MedicineBase(BaseModel):
    """Base schema for Medicine"""
    name: str = Field(..., description="Medicine name")
    notes: Optional[List[str]] = Field(default=[], description="History notes (max 3)")
    properties: Optional[str] = Field(None, description="Medicine properties/description")
    image_urls: Optional[List[str]] = Field(default=[], description="Medicine image URLs")
    dosage: Optional[str] = Field(None, description="Dosage information, e.g., '1 tablet'")
    frequency: str = Field(..., description="Frequency: 'daily', 'weekly', or comma-separated day numbers (0=Mon, 6=Sun)")
    status: Optional[str] = Field(default="active", description="Status: active, stopped, completed")
    reminder_time: List[str] = Field(..., description="List of times in HH:MM format, e.g., ['08:00', '18:00']")
    start_date: datetime = Field(..., description="Start date of medication")
    end_date: datetime = Field(..., description="End date of medication")


class MedicineCreate(MedicineBase):
    """Schema for creating a new Medicine"""
    pet_id: str = Field(..., description="Pet ID (ObjectId as string)")
    
    @field_validator('pet_id')
    @classmethod
    def validate_pet_id(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid pet_id format")
        return v


class MedicineUpdate(BaseModel):
    """Schema for updating a Medicine (Partial updates allowed)"""
    name: Optional[str] = None
    note: Optional[str] = Field(None, description="New note to add (used when status changes)")
    properties: Optional[str] = None
    image_urls: Optional[List[str]] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    status: Optional[str] = None
    reminder_time: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MedicineResponse(MedicineBase):
    """Schema for Medicine response"""
    id: str = Field(..., alias="_id", description="Medicine ID")
    user_id: str = Field(..., description="User ID")
    pet_id: str = Field(..., description="Pet ID")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
