"""
Appointments Router (SQL Version)
API Endpoints for Appointment Management
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database_sql import get_session
from app.models_sql.appointment_model import Appointment
from app.services.auth_dependency_sql import get_current_user
from app.services.appointment_service_sql import AppointmentServiceSQL
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

router = APIRouter(tags=["Appointments"])


@router.get("", summary="Get Appointments List", description="Get list of appointments for current user's pets")
async def list_appointments(
    appt_status: Optional[str] = Query(None, alias="status", description="Filter by status: Upcoming, Completed, Canceled", example="Upcoming"),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get appointments for current user's pets, optionally filtered by status."""
    try:
        if appt_status and appt_status not in ["Upcoming", "Completed", "Canceled"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid status"
            )
        
        # Query with pet details
        conditions = [
            Appointment.user_id == current_user["user_id"],
            Appointment.is_deleted == False
        ]
        
        if appt_status:
            conditions.append(Appointment.status == appt_status)
        
        result = await session.execute(
            select(Appointment)
            .options(selectinload(Appointment.pet))
            .where(and_(*conditions))
            .order_by(Appointment.appointment_date.asc())
        )
        appointments = result.scalars().all()
        
        # Build response with pet info and separated date/time
        data = []
        for appt in appointments:
            appointment_date_str = appt.appointment_date.strftime("%Y-%m-%d") if appt.appointment_date else ""
            appointment_time_str = appt.appointment_date.strftime("%H:%M") if appt.appointment_date else ""
            
            data.append({
                "appointment_id": appt.appointment_id,
                "pet_id": appt.pet_id,
                "pet_name": appt.pet.name if appt.pet else "",
                "pet_image": appt.pet.profile_image if appt.pet else "",
                "location": appt.location,
                "appointment_date": appointment_date_str,
                "appointment_time": appointment_time_str,
                "status": appt.status,
            })
        
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{appointment_id}", summary="Get Appointment Detail", description="Get detailed information about a specific appointment")
async def get_appointment_detail(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get detailed information about a specific appointment. Returns 403 if not owned by current user."""
    appt = await AppointmentServiceSQL.get_appointment_by_id(session, appointment_id)
    
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Verify ownership
    if appt.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "success": True,
        "data": {
            "appointment_id": appt.appointment_id,
            "pet_id": appt.pet_id,
            "user_id": appt.user_id,
            "pet_name": appt.pet.name if appt.pet else "",
            "pet_image": appt.pet.profile_image if appt.pet else "",
            "location": appt.location,
            "appointment_date": appt.appointment_date.isoformat() if appt.appointment_date else None,
            "status": appt.status,
            "note": appt.note or "",
            "created_at": appt.created_at.isoformat() if appt.created_at else None,
            "updated_at": appt.updated_at.isoformat() if appt.updated_at else None
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create Appointment", description="Create a new appointment with notification")
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a new appointment and auto-generate a notification."""
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
    """Update appointment fields. Regenerates notification if date or location changes."""
    result = await AppointmentServiceSQL.update_appointment(
        session,
        appointment_id,
        current_user["user_id"],
        appointment_data.model_dump(exclude_unset=True)
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
    """Cancel appointment by setting status to 'Canceled'."""
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
    """Permanently delete an appointment and its associated notification."""
    success = await AppointmentServiceSQL.delete_appointment(
        session,
        appointment_id,
        current_user["user_id"]
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"success": True, "message": "Appointment deleted successfully"}
