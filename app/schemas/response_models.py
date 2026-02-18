"""
Response Models for API Documentation (Swagger/OpenAPI)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Union


# === Base Response Models ===

class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Error message here"
            }
        }
    )


# === Medicine/Notification Response Models ===

class NotificationItem(BaseModel):
    """Individual notification in list"""
    notification_id: int = Field(..., description="Notification ID")
    notification_at: str = Field(..., description="Notification time (ISO format)")
    istaken: bool = Field(..., description="Whether medicine was taken")
    pet_id: int = Field(..., description="Pet ID")
    
    # Additional fields for frontend
    pet_name: Optional[str] = Field(None, description="Pet name")
    pet_image: Optional[str] = Field(None, description="Pet profile image URL")
    medicine_id: Optional[int] = Field(None, description="Medicine ID")
    medicine_name: Optional[str] = Field(None, description="Medicine name")
    dosage: Optional[str] = Field(None, description="Medicine dosage")
    medicine_frequency: Optional[str] = Field(None, description="Medicine frequency")
    reminder_time: Optional[List[str]] = Field(default_factory=list, description="Reminder times")
    user_id: Optional[str] = Field(None, description="User ID")
    status: Optional[str] = Field(None, description="Medicine status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notification_id": 1,
                "title": "Time to give Amoxicillin to Lucky",
                "notification_at": "2026-02-08T08:00:00",
                "istaken": False,
                "pet_id": 1,
                "pet_name": "Lucky",
                "pet_image": "https://example.com/lucky.jpg",
                "medicine_id": 1,
                "medicine_name": "Amoxicillin",
                "dosage": "250mg",
                "reminder_time": ["08:00", "20:00"]
            }
        }
    )



class ReminderSlot(BaseModel):
    """Individual reminder slot"""
    notification_id: int
    time: str
    status: str # "taken", "pending", "missed"
    taken_at: Optional[str] = None

class GroupedMedicineNotification(BaseModel):
    """Grouped medicine notification"""
    medicine_id: int
    pet_id: int
    pet_name: str
    pet_image: Optional[str] = None
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reminder_time: List[str] = []
    reminders: List[ReminderSlot]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    note: Optional[str] = None

class NotificationListResponse(BaseModel):
    """Response for GET /v1/medications"""
    success: bool = True
    data: List[GroupedMedicineNotification]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [
                    {
                        "medicine_id": 1,
                        "pet_id": 1,
                        "pet_name": "Lucky",
                        "pet_image": "https://example.com/lucky.jpg",
                        "medicine_name": "Amoxicillin",
                        "dosage": "2 tablets",
                        "reminders": [
                            {
                                "notification_id": 1,
                                "time": "08:00",
                                "status": "taken"
                            },
                             {
                                "notification_id": 2,
                                "time": "20:00",
                                "status": "pending"
                            }
                        ]
                    }
                ]
            }
        }
    )


class NotificationDetail(BaseModel):
    """Detailed notification information"""
    notification_id: int
    title: str
    notification_at: str
    istaken: bool
    taken_at: Optional[str] = None
    pet_id: int
    pet_name: Optional[str] = None
    pet_image: Optional[str] = None
    medicine_id: int
    medicine_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reminder_time: List[str] = []
    time_per_day: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notification_id": 1,
                "title": "Time to give Amoxicillin to Lucky",
                "notification_at": "2026-02-08T08:00:00",
                "istaken": True,
                "taken_at": "2026-02-08T22:07:04",
                "pet_id": 1,
                "pet_name": "Lucky",
                "pet_image": "https://example.com/lucky.jpg",
                "medicine_id": 1,
                "medicine_name": "Amoxicillin",
                "dosage": "2 tablets",
                "frequency": "-1",
                "reminder_time": ["08:00", "20:00"],
                "time_per_day": 2
            }
        }
    )


class NotificationDetailResponse(BaseModel):
    """Response for GET /v1/medications/{id}"""
    success: bool = True
    data: NotificationDetail


class MedicineItem(BaseModel):
    """Medicine information"""
    medicine_id: int
    name: str
    dosage: Optional[str]
    frequency: str
    status: str
    start_date: str
    end_date: str
    pet_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "medicine_id": 5,
                "name": "Amoxicillin",
                "dosage": "1 tablet",
                "frequency": "-1",
                "status": "TAKE",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
                "pet_id": 2
            }
        }
    )


class MedicineListResponse(BaseModel):
    """Response for GET /v1/medications/medicines/by-pet/{pet_id}"""
    success: bool = True
    data: List[MedicineItem]


class MedicineCreateResponse(BaseModel):
    """Response for POST /v1/medications/medicines"""
    success: bool = True
    message: str
    medicine_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Medicine created successfully",
                "medicine_id": 5
            }
        }
    )


# === Appointment Response Models ===

class AppointmentItem(BaseModel):
    """Individual appointment in list"""
    appointment_id: int
    pet_id: int
    pet_name: Optional[str] = None
    pet_image: Optional[str] = None
    location: str
    appointment_date: str
    appointment_time: Optional[str] = None
    status: str
    note: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "appointment_id": 1,
                "pet_id": 1,
                "pet_name": "Lucky",
                "pet_image": "https://example.com/lucky.jpg",
                "location": "โรงพยาบาลสัตว์ ABC",
                "appointment_date": "2026-02-15",
                "appointment_time": "14:00",
                "status": "Upcoming",
                "note": "ตรวจสุขภาพประจำปี"
            }
        }
    )


class AppointmentListResponse(BaseModel):
    """Response for GET /v1/appointments"""
    success: bool = True
    data: List[dict]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [
                    {
                        "appointment_id": 1,
                        "pet_id": 1,
                        "pet_name": "Lucky",
                        "pet_image": "https://example.com/lucky.jpg",
                        "location": "โรงพยาบาลสัตว์ ABC",
                        "appointment_date": "2026-02-15",
                        "appointment_time": "14:00",
                        "status": "Upcoming",
                        "note": "ตรวจสุขภาพประจำปี"
                    }
                ]
            }
        }
    )


class AppointmentDetailData(BaseModel):
    """Detailed appointment information"""
    appointment_id: int
    pet_id: int
    user_id: int
    location: str
    appointment_date: str
    status: str
    note: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "appointment_id": 1,
                "pet_id": 1,
                "user_id": 2,
                "location": "โรงพยาบาลสัตว์ ABC",
                "appointment_date": "2026-02-15T14:00:00",
                "status": "Upcoming",
                "note": "ตรวจสุขภาพประจำปี",
                "created_at": "2026-02-08T10:00:00",
                "updated_at": "2026-02-08T10:00:00"
            }
        }
    )


class AppointmentDetailResponse(BaseModel):
    """Response for GET /v1/appointments/{id}"""
    success: bool = True
    data: AppointmentDetailData


class AppointmentCreateResponse(BaseModel):
    """Response for POST /v1/appointments"""
    success: bool = True
    message: str
    appointment_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Appointment created successfully",
                "appointment_id": 1
            }
        }
    )


# === Pet Response Models ===

class PetItem(BaseModel):
    """Pet information"""
    pet_id: int
    name: str
    species: str
    breed: Optional[str] = None
    birth_date: Optional[str] = None
    weight_kg: Optional[float] = None
    color: Optional[str] = None
    gender: Optional[str] = None
    in_medical: Optional[bool] = None
    infecund: Optional[bool] = None
    profile_image: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pet_id": 1,
                "name": "Lucky",
                "species": "Dog",
                "breed": "Golden Retriever",
                "birth_date": "2023-06-15",
                "weight_kg": 25.5,
                "color": "Golden",
                "gender": "Male",
                "in_medical": False,
                "infecund": False,
                "profile_image": "https://example.com/lucky.jpg"
            }
        }
    )


class PetListResponse(BaseModel):
    """Response for GET /v1/pets"""
    data: List[PetItem]


class PetRegisterResponse(BaseModel):
    """Response for POST /v1/pets"""
    message: str
    pet_id: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Pet registered successfully",
                "pet_id": 2
            }
        }
    )


# === Dashboard Response Models ===

class DashboardPet(BaseModel):
    """Pet info in dashboard"""
    pet_id: int
    name: str
    species: Optional[str] = None
    breed: Optional[str] = None
    in_medical: Optional[bool] = None
    profile_image: Optional[str] = None


class DashboardNotification(BaseModel):
    """Notification in dashboard"""
    notification_id: int
    title: str
    medicine_id: int
    medicine_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reminder_time: List[str] = []
    time_per_day: int = 0
    pet_id: int
    pet_name: Optional[str] = None
    pet_image: Optional[str] = None
    notification_at: str
    istaken: bool


class DashboardAppointment(BaseModel):
    """Appointment in dashboard"""
    appointment_id: int
    pet_id: int
    pet_name: Optional[str] = None
    pet_image: Optional[str] = None
    location: Optional[str] = None
    appointment_date: str
    appointment_time: Optional[str] = None
    status: str
    note: Optional[str] = None


class DashboardData(BaseModel):
    """Dashboard data"""
    fname: str
    lname: str
    profile_image: Optional[str] = None
    pets: List[DashboardPet]
    medicines_notifications: List[DashboardNotification]
    appointments: List[DashboardAppointment]


class DashboardResponse(BaseModel):
    """Response for GET /v1/dashboard/home"""
    success: bool = True
    data: DashboardData
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": {
                    "fname": "สมชาย",
                    "lname": "รักสัตว์",
                    "profile_image": "https://profile.line-scdn.net/...",
                    "pets": [
                        {
                            "pet_id": 1,
                            "name": "Lucky",
                            "species": "Dog",
                            "breed": "Golden Retriever",
                            "in_medical": False,
                            "profile_image": "https://example.com/lucky.jpg"
                        }
                    ],
                    "medicines_notifications": [
                        {
                            "notification_id": 1,
                            "title": "Time to give Amoxicillin to Lucky",
                            "medicine_id": 1,
                            "medicine_name": "Amoxicillin",
                            "dosage": "2 tablets",
                            "frequency": "-1",
                            "reminder_time": ["08:00"],
                            "time_per_day": 1,
                            "pet_id": 1,
                            "pet_name": "Lucky",
                            "pet_image": "https://example.com/lucky.jpg",
                            "notification_at": "2026-02-08T08:00:00",
                            "istaken": False
                        }
                    ],
                    "appointments": [
                        {
                            "appointment_id": 1,
                            "pet_id": 1,
                            "pet_name": "Lucky",
                            "pet_image": "https://example.com/lucky.jpg",
                            "location": "โรงพยาบาลสัตว์ ABC",
                            "appointment_date": "2026-02-15",
                            "appointment_time": "14:00",
                            "status": "Upcoming",
                            "note": "ตรวจสุขภาพประจำปี"
                        }
                    ]
                }
            }
        }
    )


# === Upload Response Models ===

class UploadResponse(BaseModel):
    """Response for image upload"""
    success: bool = True
    url: str
    filename: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "url": "https://pub-xxxxx.r2.dev/pets/uuid-123.jpg",
                "filename": "pets/uuid-123.jpg"
            }
        }
    )


class DeleteImageResponse(BaseModel):
    """Response for image deletion"""
    success: bool = True
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Image deleted successfully"
            }
        }
    )


# === User Profile Response Models ===

class UserProfileData(BaseModel):
    """User profile information"""
    user_id: int
    fname: str
    lname: str
    line_id: str
    profile_image: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 2,
                "fname": "สมชาย",
                "lname": "รักสัตว์",
                "line_id": "U1234567890abcdef",
                "profile_image": "https://profile.line-scdn.net/..."
            }
        }
    )


class UserProfileResponse(BaseModel):
    """Response for GET /v1/user/profile"""
    success: bool = True
    data: UserProfileData


class UserProfileUpdateResponse(BaseModel):
    """Response for PATCH /v1/user/profile"""
    success: bool = True
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Profile updated successfully"
            }
        }
    )
