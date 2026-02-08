from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class OwnerRegister(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    address_line1: str
    address_line2: Optional[str] = None
    subdistrict: str
    district: str
    province: str
    postal_code: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "สมชาย",
                "last_name": "ใจดี",
                "phone": "0812345678",
                "email": "somchai@example.com",
                "address_line1": "123 ถนนสุขุมวิท",
                "address_line2": "แขวงคลองเตย",
                "subdistrict": "คลองเตย",
                "district": "คลองเตย",
                "province": "กรุงเทพมหานคร",
                "postal_code": "10110"
            }
        }
    )

class PetRegister(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    gender: str
    birth_date: str 
    color: Optional[str] = None
    weight_kg: float = 0.0
    infecund: bool = False
    in_medical: bool = False
    profile_image: Optional[str] = None  
    previous_clinic: Optional[str] = None 
    has_medical_history: bool = False
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ลัคกี้",
                "species": "Dog",
                "breed": "Golden Retriever",
                "gender": "Male",
                "birth_date": "2022-03-15",
                "color": "Golden",
                "weight_kg": 25.5,
                "infecund": False,
                "in_medical": False,
                "profile_image": "https://example.com/pets/lucky.jpg",
                "previous_clinic": "คลินิกสัตว์เลี้ยงแสนรัก",
                "has_medical_history": True
            }
        }
    )   