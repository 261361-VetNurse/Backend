from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class PetNoteCreate(BaseModel):
    note: str = Field(..., example="น้องซึม ไม่ยอมทานอาหารเช้า")
    tags: List[str] = Field(default_factory=list, example=["ซึม", "เบื่ออาหาร"])
    images: List[str] = Field(default_factory=list, example=["https://storage.com/image1.jpg"])

class PetUpdateSchema(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    weight_kg: Optional[float] = None
    allergies: Optional[list] = None
    profile_image: Optional[str] = None 
    color: Optional[str] = None
    infecund: Optional[bool] = None
    in_medical: Optional[bool] = None
    note: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Lucky Jr.",
                "weight_kg": 28.5,
                "breed": "Golden Retriever Mix",
                "in_medical": True,
                "profile_image": "https://example.com/new-image.jpg"
            }
        }
    )

class MedicalHistoryCreate(BaseModel):
    date: str = Field(..., example="2026-01-11")
    time: str = Field(..., example="14:00")
    note: str = Field(..., example="รายละเอียดการรักษาที่ผู้ใช้กรอกเอง")