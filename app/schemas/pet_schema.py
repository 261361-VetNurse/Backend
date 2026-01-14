from pydantic import BaseModel, Field
from typing import Optional, List , Literal
from datetime import datetime


AppointmentStatus = Literal["upcoming", "completed", "cancelled"]
MedicationStatus = Literal["active", "stop"]

# --- Schema สำหรับระบบนัดหมาย (Appointments) ---
class AppointmentCreate(BaseModel):
    appointment_date: str = Field(..., example="2026-02-15")
    appointment_time: str = Field(..., example="10:00")
    note: Optional[str] = None
    purpose: str = Field(..., example="ตรวจสุขภาพประจำปี")
    location: Optional[str] = Field(None, example="ห้องตรวจ A") 
    status: AppointmentStatus = Field(default="upcoming") 
    reminder_time: Optional[str] = Field(None, example="1 วันก่อนนัด")

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

class MedicationCreate(BaseModel):
    drug_id: Optional[str] = Field(None, example="65a123...") 
    drug_name: str = Field(..., example="Amoxicillin")
    dosage: str = Field(..., example="1 เม็ด")
    frequency: str = Field(..., example="เช้า-เย็น หลังอาหาร")
    status: MedicationStatus = Field(default="active")
    start_date: str = Field(..., example="2026-01-10")
    end_date: Optional[str] = Field(None, example="2026-01-15")
    reminder_time: List[str] = Field(default_factory=list, example=["08:00", "20:00"])
    notes_id: Optional[str] = None
    instructions: Optional[str] = Field(None, example="กินให้ครบ 5 วัน")

class MedicalHistoryCreate(BaseModel):
    date: str = Field(..., example="2026-01-11")
    time: str = Field(..., example="14:00")
    note: str = Field(..., example="รายละเอียดการรักษาที่ผู้ใช้กรอกเอง")