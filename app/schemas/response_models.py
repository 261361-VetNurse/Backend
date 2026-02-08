"""
Response Models for API Documentation (Swagger/OpenAPI)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime


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
    title: str = Field(..., description="Notification title")
    notification_at: str = Field(..., description="Notification time (ISO format)")
    istaken: bool = Field(..., description="Whether medicine was taken")
    pet_id: int = Field(..., description="Pet ID")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "_id": 1,
                "notification_id": 1,
                "title": "ยา Amoxicillin - 08:00 น.",
                "notification_at": "2026-02-08T08:00:00",
                "istaken": False,
                "pet_id": 2
            }
        }
    )


class NotificationListResponse(BaseModel):
    """Response for GET /v1/medications"""
    success: bool = True
    data: List[NotificationItem]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [
                    {
                        "_id": 1,
                        "notification_id": 1,
                        "title": "ยา Amoxicillin - 08:00 น.",
                        "notification_at": "2026-02-08T08:00:00",
                        "istaken": False,
                        "pet_id": 2
                    }
                ]
            }
        }
    )


class NotificationDetail(BaseModel):
    """Detailed notification information"""
    notification_id: int
    medicine_id: int
    pet_id: int
    user_id: int
    title: str
    notification_at: str
    istaken: bool
    status: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notification_id": 1,
                "medicine_id": 5,
                "pet_id": 2,
                "user_id": 10,
                "title": "ยา Amoxicillin - 08:00 น.",
                "notification_at": "2026-02-08T08:00:00",
                "istaken": False,
                "status": "pending"
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
    location: str
    appointment_date: str
    status: str
    note: Optional[str]
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": 1,
                "appointment_id": 1,
                "pet_id": 2,
                "location": "ABC Veterinary Clinic",
                "appointment_date": "2026-02-15T14:00:00",
                "status": "Upcoming",
                "note": "Annual checkup"
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
                        "_id": 1,
                        "appointment_id": 1,
                        "pet_id": 2,
                        "location": "ABC Veterinary Clinic",
                        "appointment_date": "2026-02-15T14:00:00",
                        "status": "Upcoming",
                        "note": "Annual checkup"
                    }
                ]
            }
        }
    )


class AppointmentDetailData(BaseModel):
    """Detailed appointment information"""
    appointment_id: int
    pet_id: int
    pet_name: Optional[str]
    location: str
    appointment_date: str
    status: str
    note: Optional[str]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "appointment_id": 1,
                "pet_id": 2,
                "pet_name": "Lucky",
                "location": "ABC Veterinary Clinic",
                "appointment_date": "2026-02-15T14:00:00",
                "status": "Upcoming",
                "note": "Annual checkup"
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
    breed: Optional[str]
    age: Optional[float]
    weight: Optional[float]
    profile_image: Optional[str]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pet_id": 2,
                "name": "Lucky",
                "species": "Dog",
                "breed": "Golden Retriever",
                "age": 3.5,
                "weight": 25.5,
                "profile_image": "https://example.com/image.jpg"
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
    pet_id: str
    name: str
    profile_image: str


class DashboardNotification(BaseModel):
    """Notification in dashboard"""
    notification_id: str
    title: str
    medicine_id: str
    medicine_name: str
    pet_id: str
    pet_name: str
    pet_image: str
    notification_at: datetime
    status: str
    istaken: bool


class DashboardAppointment(BaseModel):
    """Appointment in dashboard"""
    _id: str
    pet_id: str
    pet_name: str
    pet_image: str
    appointment_date: datetime
    status: str
    notification_status: str
    note: str


class DashboardData(BaseModel):
    """Dashboard data"""
    fname: str
    lname: str
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
                    "fname": "John",
                    "lname": "Doe",
                    "pets": [
                        {
                            "pet_id": "2",
                            "name": "Lucky",
                            "profile_image": "https://example.com/image.jpg"
                        }
                    ],
                    "medicines_notifications": [],
                    "appointments": []
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
    profile_image: Optional[str]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 10,
                "fname": "John",
                "lname": "Doe",
                "line_id": "U1234567890",
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
