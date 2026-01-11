from pydantic import BaseModel, EmailStr
from typing import Optional

# สำหรับลงทะเบียนเจ้าของ 
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

# สำหรับลงทะเบียนสัตว์เลี้ยงใหม่
class PetRegister(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    gender: str
    birth_date: str 
    color: Optional[str] = None
    weight_kg: float = 0.0
    infecund: bool = False
    profile_image: Optional[str] = None  
    previous_clinic: Optional[str] = None 
    has_medical_history: bool = False   