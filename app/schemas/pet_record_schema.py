"""
Pet Record Schemas (Symptom Records)
Pydantic schemas for pet health and behavior records
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class PetRecordCreate(BaseModel):
    """Schema for creating new pet record"""
    pet_id: int = Field(..., description="Pet ID", example=1)
    note: str = Field(..., description="Health or behavior note", example="พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร")
    note_image: Optional[List[str]] = Field(default=[], description="Array of image URLs (max 4)", max_length=4, example=["https://example.com/image1.jpg"])
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pet_id": 1,
                "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร และดื่มน้ำน้อยกว่าปกติ",
                "note_image": [
                    "https://cloudflare.example.com/pet-records/image1.jpg",
                    "https://cloudflare.example.com/pet-records/image2.jpg"
                ]
            }
        }
    )


class PetRecordUpdate(BaseModel):
    """Schema for updating pet record"""
    note: Optional[str] = Field(None, description="Updated note", example="อาการดีขึ้นหลังให้ยา")
    note_image: Optional[List[str]] = Field(None, description="Updated image URLs (max 4)", max_length=4)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "note": "อาการดีขึ้นมากหลังจากให้ยาและดูแลเป็นพิเศษ 2 วัน",
                "note_image": [
                    "https://cloudflare.example.com/pet-records/updated1.jpg"
                ]
            }
        }
    )


class PetRecordResponse(BaseModel):
    """Schema for pet record response with full details"""
    record_id: int = Field(..., description="Record ID")
    pet_id: int = Field(..., description="Pet ID")
    pet_name: str = Field(..., description="Pet name")
    pet_image: str = Field(..., description="Pet profile image URL")
    date_added: str = Field(..., description="Date added (YYYY-MM-DD)")
    time_added: str = Field(..., description="Time added (HH:MM)")
    note: str = Field(..., description="Record note")
    note_image: List[str] = Field(default=[], description="Array of image URLs")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "record_id": 1,
                "pet_id": 1,
                "pet_name": "ลัคกี้",
                "pet_image": "https://example.com/lucky.jpg",
                "date_added": "2026-02-08",
                "time_added": "14:30",
                "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร",
                "note_image": [
                    "https://cloudflare.example.com/pet-records/image1.jpg",
                    "https://cloudflare.example.com/pet-records/image2.jpg"
                ]
            }
        }
    )


class PetRecordCalendarResponse(BaseModel):
    """Schema for calendar view of pet records (simplified)"""
    record_id: int = Field(..., description="Record ID")
    pet_id: int = Field(..., description="Pet ID")
    pet_name: str = Field(..., description="Pet name")
    pet_image: str = Field(..., description="Pet profile image URL")
    note: str = Field(..., description="Record note")
    note_image: List[str] = Field(default=[], description="Array of image URLs")
    time_added: str = Field(..., description="Timestamp when added")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "record_id": 1,
                "pet_id": 1,
                "pet_name": "ลัคกี้",
                "pet_image": "https://example.com/lucky.jpg",
                "note": "พบว่าสัตว์เลี้ยงมีอาการเบื่ออาหาร",
                "note_image": ["https://example.com/image1.jpg"],
                "time_added": "2026-02-08T14:30:00"
            }
        }
    )
