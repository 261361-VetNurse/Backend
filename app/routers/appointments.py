"""
Appointments Router - API Endpoints for Appointment Management

CRITICAL: These exact endpoint URLs are required by the client application.
Do not modify the URL structure.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Header
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.database import get_database
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentFeedItem,
    AppointmentDetail
)
from app.services.appointment_service import AppointmentService


router = APIRouter(
    prefix="/v1/appointments",
    tags=["Appointments"]
)


def get_db():
    """Dependency to get database instance"""
    return get_database()


async def get_current_user_id(
    access_token: str = Header(..., alias="access_token", description="JWT access token"),
    db = Depends(get_db)
) -> ObjectId:
    """
    Dependency to get current user ID from access token
    
    Raises:
        HTTPException: If token is invalid or expired
        
    Returns:
        ObjectId of current user
    """
    # Validate JWT token
    jwt_record = await db.JWT.find_one({"access_token": access_token})
    if not jwt_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    # Check if token is expired
    if jwt_record.get("expires_in") and jwt_record["expires_in"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired"
        )
    
    user_id_str = jwt_record["user_id"]
    return ObjectId(user_id_str)


# ============================================================================
# Appointment Endpoints
# ============================================================================

@router.get("", response_model=dict)
async def list_appointments(
    status: Optional[str] = Query(None, description="Filter by status (Upcoming, Completed, Canceled)"),
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    GET /v1/appointments - Get Appointment List
    
    Returns list of appointments for the current user.
    
    Query Parameters:
    - status (optional): Filter by status ("Upcoming", "Completed", "Canceled")
    
    Access Control:
    - Returns only appointments belonging to current user
    
    Returns:
    - List of AppointmentFeedItem (lightweight view)
    """
    try:
        # Validate status if provided
        if status and status not in ["Upcoming", "Completed", "Canceled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be one of: Upcoming, Completed, Canceled"
            )
        
        # Get appointments
        appointments = await AppointmentService.get_user_appointments(
            db, user_id, status_filter=status
        )
        
        # Format response (lightweight feed items)
        result = []
        for appt in appointments:
            result.append({
                "_id": str(appt["_id"]),
                "note": appt.get("note"),
                "pet_id": str(appt["pet_id"]),
                "appointment_date": appt["appointment_date"],
                "status": appt["status"]
            })
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching appointments: {str(e)}"
        )


@router.get("/{appointment_id}", response_model=dict)
async def get_appointment_detail(
    appointment_id: str,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    GET /v1/appointments/{appointment_id} - Get Appointment Details
    
    Returns full appointment details.
    
    Access Control:
    - Verifies appointment belongs to current user
    """
    try:
        # Validate ObjectId
        try:
            appt_id = ObjectId(appointment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid appointment ID format"
            )
        
        # Get appointment
        appointment = await AppointmentService.get_appointment_by_id(db, appt_id, user_id)
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Format response
        result = {
            "_id": str(appointment["_id"]),
            "pet_id": str(appointment["pet_id"]),
            "location": appointment["location"],
            "appointment_date": appointment["appointment_date"],
            "status": appointment["status"],
            "note": appointment.get("note"),
            "created_at": appointment["created_at"],
            "updated_at": appointment["updated_at"]
        }
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching appointment: {str(e)}"
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    POST /v1/appointments - Create New Appointment
    
    Automatically generates a notification 2 days before the appointment date.
    
    Access Control:
    - Verifies pet belongs to current user
    """
    try:
        # Verify pet ownership
        pet_id = ObjectId(appointment.pet_id)
        if not await AppointmentService.verify_pet_ownership(db, pet_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pet does not belong to current user"
            )
        
        # Create appointment with notification
        result = await AppointmentService.create_appointment_with_notification(
            db=db,
            user_id=user_id,
            pet_id=pet_id,
            location=appointment.location,
            appointment_date=appointment.appointment_date,
            status=appointment.status,
            note=appointment.note
        )
        
        return {
            "success": True,
            "message": "Appointment created successfully",
            "data": {
                "appointment_id": str(result["appointment_id"]),
                "notification_id": str(result["notification_id"]),
                "notification_at": result["notification_at"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating appointment: {str(e)}"
        )


@router.patch("/{appointment_id}/edit", response_model=dict)
async def edit_appointment(
    appointment_id: str,
    appointment_update: AppointmentUpdate,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    PATCH /v1/appointments/{appointment_id}/edit - Update Appointment
    
    Handles side effects:
    - If appointment_date changes -> Updates notification_at (new_date - 2 days)
    - If location changes -> Updates notification title
    
    Access Control:
    - Verifies appointment belongs to current user
    """
    try:
        # Validate ObjectId
        try:
            appt_id = ObjectId(appointment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid appointment ID format"
            )
        
        # Prepare update data (exclude None values)
        update_data = appointment_update.model_dump(exclude_none=True)
        
        if not update_data:
            return {
                "success": True,
                "message": "No fields to update",
                "data": {}
            }
        
        # Execute update
        result = await AppointmentService.update_appointment(
            db, appt_id, user_id, update_data
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Appointment not found")
            )
        
        return {
            "success": True,
            "message": "Appointment updated successfully",
            "data": {
                "appointment_id": appointment_id,
                "notification_updated": result.get("notification_updated", False),
                "notification_title_updated": result.get("notification_title_updated", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating appointment: {str(e)}"
        )


@router.patch("/{appointment_id}/cancel", response_model=dict)
async def cancel_appointment(
    appointment_id: str,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    PATCH /v1/appointments/{appointment_id}/cancel - Cancel Appointment
    
    Changes status to "Canceled" and cancels the notification.
    
    Access Control:
    - Verifies appointment belongs to current user
    """
    try:
        # Validate ObjectId
        try:
            appt_id = ObjectId(appointment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid appointment ID format"
            )
        
        # Cancel appointment
        result = await AppointmentService.cancel_appointment(db, appt_id, user_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Appointment not found")
            )
        
        return {
            "success": True,
            "message": result["message"],
            "data": {
                "appointment_id": appointment_id,
                "status": "Canceled"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canceling appointment: {str(e)}"
        )


@router.delete("/{appointment_id}", response_model=dict)
async def delete_appointment(
    appointment_id: str,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    DELETE /v1/appointments/{appointment_id} - Delete Appointment
    
    Hard deletes the appointment and its notification.
    
    Access Control:
    - Verifies appointment belongs to current user
    """
    try:
        # Validate ObjectId
        try:
            appt_id = ObjectId(appointment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid appointment ID format"
            )
        
        # Delete appointment
        result = await AppointmentService.delete_appointment(db, appt_id, user_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Appointment not found")
            )
        
        return {
            "success": True,
            "message": "Appointment and related notifications deleted successfully",
            "data": {
                "appointment_id": appointment_id,
                "appointment_deleted": result["appointment_deleted"],
                "notifications_deleted": result["notifications_deleted"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting appointment: {str(e)}"
        )
