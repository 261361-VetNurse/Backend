"""
Medications Router - API Endpoints for Medicine & Notification Management

CRITICAL: These exact endpoint URLs are required by the client application.
Do not modify the URL structure.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Header
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.database import get_database
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineResponse
from app.schemas.notification import NotificationFeedItem, NotificationDetail, MarkTakenRequest
from app.services.medicine_service import MedicineService
from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/v1/medications",
    tags=["Medications"]
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
# GROUP A: Notification Feed & Actions
# ============================================================================

@router.get("", response_model=dict)
async def list_medications(
    pets_id: Optional[str] = Query(None, description="Filter by pet ID (optional)"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD, default: today)"),
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    GET /v1/medications - Notification Feed / Overview
    
    Returns lightweight list of notifications (NotificationFeedItem).
    
    Query Parameters:
    - pets_id (optional): Filter notifications for a specific pet
    - date (optional): Filter notifications for a specific date (YYYY-MM-DD, default: today)
    
    Access Control:
    - If pets_id provided: Verify pet belongs to current user
    - If pets_id missing: Return notifications for ALL user's pets
    
    Returns:
    - List of NotificationFeedItem (id, title, notification_at, istaken, pet_id)
    """
    try:
        # Parse date parameter or use today
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            filter_date = datetime.utcnow()
        
        # Determine which pets to query
        if pets_id:
            # Verify pet ownership
            try:
                pet_id = ObjectId(pets_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid pet_id format"
                )
            
            if not await MedicineService.verify_pet_ownership(db, pet_id, user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Pet does not belong to current user"
                )
            pet_ids = [pet_id]
        else:
            # Get all pets belonging to user
            pet_ids = await MedicineService.get_user_pet_ids(db, user_id)
            if not pet_ids:
                return {
                    "success": True,
                    "data": []
                }
        
        # Get notifications
        notifications = await NotificationService.get_notifications_by_date(
            db, pet_ids, filter_date
        )
        
        # Format response (lightweight feed items)
        result = []
        for notif in notifications:
            result.append({
                "_id": str(notif["_id"]),
                "title": notif["title"],
                "notification_at": notif["notification_at"],
                "istaken": notif.get("istaken", False),
                "pet_id": str(notif["pet_id"])
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
            detail=f"Error fetching medications: {str(e)}"
        )


@router.get("/{notification_id}", response_model=dict)
async def get_medication_detail(
    notification_id: str,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    GET /v1/medications/{notification_id} - View Notification Details
    
    Returns full MEDICINES_NOTIFICATION document (NotificationDetail).
    
    Access Control:
    - Verifies notification belongs to current user
    """
    try:
        # Validate ObjectId
        try:
            notif_id = ObjectId(notification_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification ID format"
            )
        
        # Verify ownership
        if not await NotificationService.verify_notification_belongs_to_user(db, notif_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Notification does not belong to you"
            )
        
        # Fetch notification
        notification = await NotificationService.get_notification_by_id(db, notif_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Format response (full detail)
        result = {
            "_id": str(notification["_id"]),
            "pet_id": str(notification["pet_id"]),
            "user_id": str(notification["user_id"]),
            "medicine_id": str(notification["medicine_id"]),
            "title": notification["title"],
            "notification_at": notification["notification_at"],
            "sending_status": notification.get("sending_status", "not_sent"),
            "status": notification.get("status", "pending"),
            "sending_count": notification.get("sending_count", 0),
            "istaken": notification.get("istaken", False),
            "created_at": notification["created_at"],
            "updated_at": notification["updated_at"]
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
            detail=f"Error fetching notification detail: {str(e)}"
        )


@router.patch("/{notification_id}/taken", response_model=dict)
async def mark_medication_taken(
    notification_id: str,
    request: Optional[MarkTakenRequest] = None,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    PATCH /v1/medications/{notification_id}/taken - Mark as Done
    
    Updates the 'istaken' field.
    
    Access Control:
    - Verifies notification belongs to current user
    """
    try:
        # Validate ObjectId
        try:
            notif_id = ObjectId(notification_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification ID format"
            )
        
        # Verify ownership
        if not await NotificationService.verify_notification_belongs_to_user(db, notif_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Notification does not belong to you"
            )
        
        # Determine istaken value
        istaken_value = True
        if request and request.istaken is not None:
            istaken_value = request.istaken
        
        # Update notification
        success = await NotificationService.mark_notification_taken(db, notif_id, istaken_value)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or already updated"
            )
        
        return {
            "success": True,
            "message": f"Medicine marked as {'taken' if istaken_value else 'not taken'}",
            "data": {
                "notification_id": notification_id,
                "istaken": istaken_value
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notification: {str(e)}"
        )


# ============================================================================
# GROUP B: Medicine Management (Accessed via Notification)
# ============================================================================

@router.get("/{notification_id}/{medicine_id}", response_model=dict)
async def get_medicine_detail(
    notification_id: str,
    medicine_id: str,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    GET /v1/medications/{notification_id}/{medicine_id} - Get Root Medicine Details
    
    Returns full MEDICINES document.
    
    Security:
    - Validates notification -> medicine -> user ownership chain
    - Ensures notification belongs to the specified medicine
    """
    try:
        # Validate ObjectIds
        try:
            notif_id = ObjectId(notification_id)
            med_id = ObjectId(medicine_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )
        
        # Verify complete access chain (notification -> medicine -> user)
        access_check = await MedicineService.verify_full_access_chain(
            db, notif_id, med_id, user_id
        )
        
        if not access_check["valid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=access_check["error"]
            )
        
        medicine = access_check["medicine"]
        
        # Format response
        result = {
            "_id": str(medicine["_id"]),
            "user_id": str(medicine["user_id"]),
            "pet_id": str(medicine["pet_id"]),
            "name": medicine["name"],
            "notes": medicine.get("notes", []),
            "properties": medicine.get("properties"),
            "image_urls": medicine.get("image_urls", []),
            "dosage": medicine.get("dosage"),
            "frequency": medicine["frequency"],
            "status": medicine.get("status", "TAKE"),
            "reminder_time": medicine["reminder_time"],
            "start_date": medicine["start_date"],
            "end_date": medicine["end_date"],
            "created_at": medicine["created_at"],
            "updated_at": medicine["updated_at"]
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
            detail=f"Error fetching medicine detail: {str(e)}"
        )


@router.patch("/{notification_id}/{medicine_id}/edit", response_model=dict)
async def edit_medicine(
    notification_id: str,
    medicine_id: str,
    medicine_update: MedicineUpdate,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    PATCH /v1/medications/{notification_id}/{medicine_id}/edit - Edit Medicine
    
    Handles complex side effects:
    - Scenario A: Schedule changes -> Regenerate notifications
    - Scenario B: Status -> "STOP" -> Add note, delete future notifications
    
    Security:
    - Multi-layer validation: notification -> medicine -> user chain
    - Prevents cross-medicine access attempts
    - Verifies pet ownership through medicine
    """
    try:
        # Validate ObjectIds
        try:
            notif_id = ObjectId(notification_id)
            med_id = ObjectId(medicine_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )
        
        # Verify complete access chain
        access_check = await MedicineService.verify_full_access_chain(
            db, notif_id, med_id, user_id
        )
        
        if not access_check["valid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=access_check["error"]
            )
        
        medicine = access_check["medicine"]
        
        # Additional check: Verify user owns the pet that owns this medicine
        pet_id = medicine.get("pet_id")
        if pet_id:
            if not await MedicineService.verify_pet_ownership(db, pet_id, user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Pet does not belong to you"
                )
        
        # Prepare update data (exclude None values)
        update_data = medicine_update.model_dump(exclude_none=True)
        
        if not update_data:
            return {
                "success": True,
                "message": "No fields to update",
                "data": {}
            }
        
        # Execute update with side effects
        result = await MedicineService.update_medicine(db, med_id, user_id, update_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to update medicine")
            )
        
        return {
            "success": True,
            "message": "Medicine updated successfully",
            "data": {
                "medicine_id": medicine_id,
                "notifications_deleted": result.get("notifications_deleted", 0),
                "notifications_created": result.get("notifications_created", 0),
                "note_added": result.get("note_added", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating medicine: {str(e)}"
        )


@router.patch("/{notification_id}/{medicine_id}/delete", response_model=dict)
async def delete_medicine(
    notification_id: str,
    medicine_id: str,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    PATCH /v1/medications/{notification_id}/{medicine_id}/delete - Delete Medicine
    
    Cascade deletes medicine and all related notifications.
    
    Security:
    - Full access chain verification before deletion
    - Prevents unauthorized deletion attempts
    - Validates notification-medicine relationship
    """
    try:
        # Validate ObjectIds
        try:
            notif_id = ObjectId(notification_id)
            med_id = ObjectId(medicine_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )
        
        # Verify complete access chain before allowing deletion
        access_check = await MedicineService.verify_full_access_chain(
            db, notif_id, med_id, user_id
        )
        
        if not access_check["valid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=access_check["error"]
            )
        
        # Additional check: Verify user owns the pet
        medicine = access_check["medicine"]
        pet_id = medicine.get("pet_id")
        if pet_id:
            if not await MedicineService.verify_pet_ownership(db, pet_id, user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Pet does not belong to you"
                )
        
        # Execute cascade delete
        result = await MedicineService.delete_medicine(db, med_id, user_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Medicine not found")
            )
        
        return {
            "success": True,
            "message": "Medicine and related notifications deleted successfully",
            "data": {
                "medicine_id": medicine_id,
                "medicine_deleted": result["medicine_deleted"],
                "notifications_deleted": result["notifications_deleted"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting medicine: {str(e)}"
        )


# ============================================================================
# BONUS: Create Medicine Endpoint
# ============================================================================

@router.post("/medicine", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine: MedicineCreate,
    user_id: ObjectId = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """
    POST /v1/medications/medicine - Create New Medicine
    
    Automatically generates notification records based on medication schedule.
    
    Access Control:
    - Verifies pet belongs to current user
    """
    try:
        # Verify pet ownership
        pet_id = ObjectId(medicine.pet_id)
        if not await MedicineService.verify_pet_ownership(db, pet_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pet does not belong to current user"
            )
        
        # Get pet details
        pet = await db.PETS.find_one({"_id": pet_id})
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet not found"
            )
        
        # Create medicine document
        medicine_doc = {
            "user_id": user_id,
            "pet_id": pet_id,
            "name": medicine.name,
            "notes": medicine.notes or [],
            "properties": medicine.properties,
            "image_urls": medicine.image_urls or [],
            "dosage": medicine.dosage,
            "frequency": medicine.frequency,
            "status": medicine.status or "TAKE",
            "reminder_time": medicine.reminder_time,
            "start_date": medicine.start_date,
            "end_date": medicine.end_date,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert medicine
        result = await db.MEDICINES.insert_one(medicine_doc)
        medicine_id = result.inserted_id
        
        # Generate notifications
        notification_count = await MedicineService.generate_notifications(
            db=db,
            medicine_id=medicine_id,
            user_id=user_id,
            pet_id=pet_id,
            medicine_name=medicine.name,
            pet_name=pet.get("name", "Unknown Pet"),
            start_date=medicine.start_date,
            end_date=medicine.end_date,
            frequency=medicine.frequency,
            reminder_times=medicine.reminder_time
        )
        
        return {
            "success": True,
            "message": "Medicine created successfully",
            "data": {
                "medicine_id": str(medicine_id),
                "notifications_created": notification_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating medicine: {str(e)}"
        )
