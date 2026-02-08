"""
Appointments Router (SQL Version)
API Endpoints for Appointment Management
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database_sql import get_session
from app.services.auth_dependency_sql import get_current_user
from app.services.appointment_service_sql import AppointmentServiceSQL
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

router = APIRouter(tags=["Appointments 📅"])


@router.get("", summary="Get Appointments List", description="Get list of appointments for current user's pets")
async def list_appointments(
    status: Optional[str] = Query(None, description="Filter by status: Upcoming, Completed, Canceled", example="Upcoming"),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/appointments - Get Appointments List**
    
    Get list of appointments for current user's pets.
    
    **Query Parameters:**
    - **status** (optional): Filter by status (Upcoming, Completed, Canceled)
    
    **Response:**
    ```json
    {
        "success": true,
        "data": [
            {
                "appointment_id": 1,
                "pet_id": 2,
                "location": "ABC Veterinary Clinic",
                "appointment_date": "2026-02-15T14:00:00",
                "status": "Upcoming",
                "note": "Annual checkup"
            }
        ]
    }
    ```
    """
    try:
        if status and status not in ["Upcoming", "Completed", "Canceled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        
        appointments = await AppointmentServiceSQL.get_appointments_by_user(
            session, 
            current_user["user_id"],
            status
        )
        
        return {"success": True, "data": appointments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{appointment_id}", summary="Get Appointment Detail", description="Get detailed information about a specific appointment")
async def get_appointment_detail(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **GET /v1/appointments/{appointment_id} - Appointment Details**
    
    Get detailed information about a specific appointment.
    
    **Path Parameters:**
    - **appointment_id**: Appointment ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "appointment_id": 1,
            "pet_id": 2,
            "pet_name": "Lucky",
            "location": "ABC Veterinary Clinic",
            "appointment_date": "2026-02-15T14:00:00",
            "status": "Upcoming",
            "note": "Annual checkup"
        }
    }
    ```
    """
    appointment = await AppointmentServiceSQL.get_appointment_by_id(session, appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Verify ownership
    if appointment.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"success": True, "data": appointment}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create Appointment", description="Create a new appointment with notification")
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **POST /v1/appointments - Create New Appointment**
    
    Create a new appointment. Automatically creates a notification.
    
    **Request Body:**
    ```json
    {
        "pet_id": 2,
        "location": "ABC Veterinary Clinic",
        "appointment_date": "2026-02-15T14:00:00",
        "status": "Upcoming",
        "note": "Annual checkup"
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Appointment created successfully",
        "appointment_id": 1
    }
    ```
    """
    result = await AppointmentServiceSQL.create_appointment_with_notification(
        session,
        current_user["user_id"],
        appointment_data.pet_id,
        appointment_data.location,
        appointment_data.appointment_date,
        appointment_data.status if hasattr(appointment_data, 'status') else "Upcoming",
        appointment_data.note if hasattr(appointment_data, 'note') else None
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.patch("/{appointment_id}", summary="Update Appointment", description="Update appointment information")
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **PATCH /v1/appointments/{appointment_id} - Update Appointment**
    
    Update appointment information. Regenerates notification if date changes.
    
    **Path Parameters:**
    - **appointment_id**: Appointment ID (integer)
    
    **Request Body:** (all fields optional)
    ```json
    {
        "location": "XYZ Animal Hospital",
        "appointment_date": "2026-02-16T15:00:00",
        "note": "Updated note"
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Appointment updated successfully"
    }
    ```
    """
    result = await AppointmentServiceSQL.update_appointment(
        session,
        appointment_id,
        current_user["user_id"],
        appointment_data.dict(exclude_unset=True)
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.patch("/{appointment_id}/cancel", summary="Cancel Appointment", description="Cancel an appointment (soft delete)")
async def cancel_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **PATCH /v1/appointments/{appointment_id}/cancel - Cancel Appointment**
    
    Cancel an appointment (soft delete). Sets status to 'Canceled'.
    
    **Path Parameters:**
    - **appointment_id**: Appointment ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Appointment canceled successfully"
    }
    ```
    """
    result = await AppointmentServiceSQL.cancel_appointment(
        session,
        appointment_id,
        current_user["user_id"]
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.delete("/{appointment_id}", summary="Delete Appointment", description="Delete an appointment permanently")
async def delete_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    **DELETE /v1/appointments/{appointment_id} - Delete Appointment**
    
    Permanently delete an appointment and its notification.
    
    **Path Parameters:**
    - **appointment_id**: Appointment ID (integer)
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Appointment deleted successfully"
    }
    ```
    """
    success = await AppointmentServiceSQL.delete_appointment(
        session,
        appointment_id,
        current_user["user_id"]
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"success": True, "message": "Appointment deleted successfully"}
