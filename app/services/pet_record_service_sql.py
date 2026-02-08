"""
Pet Record Service (SQL Version)
Handles CRUD operations for pet health and behavior records (symptom records)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models_sql.pet_model import Pet, PetRecord


class PetRecordServiceSQL:
    """Service class for pet record operations (SQL version)"""
    
    @staticmethod
    async def create_record(
        session: AsyncSession,
        pet_id: int,
        note: str,
        note_image: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new pet record
        
        Args:
            session: Database session
            pet_id: Pet ID
            note: Record note/description
            note_image: Optional array of image URLs (max 4)
            
        Returns:
            Dict with success status and record_id
        """
        # Verify pet exists
        result = await session.execute(
            select(Pet).where(Pet.pet_id == pet_id)
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            return {"success": False, "error": "Pet not found"}
        
        # Limit images to 4
        images = note_image[:4] if note_image else []
        
        # Create record
        record = PetRecord(
            pet_id=pet_id,
            note=note,
            images=images
        )
        
        session.add(record)
        await session.commit()
        await session.refresh(record)
        
        return {
            "success": True,
            "record_id": record.record_id,
            "created_at": record.created_at
        }
    
    @staticmethod
    async def get_record_by_id(
        session: AsyncSession,
        record_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific record by ID with pet details
        
        Args:
            session: Database session
            record_id: Record ID
            user_id: User ID for ownership verification
            
        Returns:
            Record dict with pet details or None
        """
        result = await session.execute(
            select(PetRecord)
            .options(selectinload(PetRecord.pet))
            .where(PetRecord.record_id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            return None
        
        # Verify ownership
        if record.pet.user_id != user_id:
            return None
        
        return {
            "record_id": record.record_id,
            "pet_id": record.pet_id,
            "pet_name": record.pet.name,
            "pet_image": record.pet.profile_image or "",
            "date_added": record.created_at.strftime("%Y-%m-%d") if record.created_at else "",
            "time_added": record.created_at.strftime("%H:%M") if record.created_at else "",
            "note": record.note,
            "note_image": record.images if record.images else [],
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }
    
    @staticmethod
    async def get_records_by_user(
        session: AsyncSession,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all records for user's pets (calendar view)
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            List of record dicts with pet details
        """
        # Get all user's pets
        pets_result = await session.execute(
            select(Pet).where(and_(
                Pet.user_id == user_id,
                Pet.is_deleted == False
            ))
        )
        pets = pets_result.scalars().all()
        pet_ids = [pet.pet_id for pet in pets]
        
        if not pet_ids:
            return []
        
        # Get all records for these pets
        result = await session.execute(
            select(PetRecord)
            .options(selectinload(PetRecord.pet))
            .where(PetRecord.pet_id.in_(pet_ids))
            .order_by(desc(PetRecord.created_at))
        )
        records = result.scalars().all()
        
        # Build response
        data = []
        for record in records:
            data.append({
                "record_id": record.record_id,
                "pet_id": record.pet_id,
                "pet_name": record.pet.name,
                "pet_image": record.pet.profile_image or "",
                "note": record.note,
                "note_image": record.images if record.images else [],
                "time_added": record.created_at.isoformat() if record.created_at else ""
            })
        
        return data
    
    @staticmethod
    async def update_record(
        session: AsyncSession,
        record_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a pet record
        
        Args:
            session: Database session
            record_id: Record ID
            user_id: User ID for ownership verification
            update_data: Dict with fields to update
            
        Returns:
            Dict with success status
        """
        # Get record with pet
        result = await session.execute(
            select(PetRecord)
            .options(selectinload(PetRecord.pet))
            .where(PetRecord.record_id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            return {"success": False, "error": "Record not found"}
        
        # Verify ownership
        if record.pet.user_id != user_id:
            return {"success": False, "error": "Access denied"}
        
        # Update fields
        if "note" in update_data and update_data["note"] is not None:
            record.note = update_data["note"]
        
        if "note_image" in update_data and update_data["note_image"] is not None:
            # Limit to 4 images
            record.images = update_data["note_image"][:4]
        
        await session.commit()
        await session.refresh(record)
        
        return {
            "success": True,
            "message": "Record updated successfully",
            "record_id": record.record_id
        }
    
    @staticmethod
    async def delete_record(
        session: AsyncSession,
        record_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete a pet record (hard delete)
        
        Args:
            session: Database session
            record_id: Record ID
            user_id: User ID for ownership verification
            
        Returns:
            Dict with success status
        """
        # Get record with pet
        result = await session.execute(
            select(PetRecord)
            .options(selectinload(PetRecord.pet))
            .where(PetRecord.record_id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            return {"success": False, "error": "Record not found"}
        
        # Verify ownership
        if record.pet.user_id != user_id:
            return {"success": False, "error": "Access denied"}
        
        await session.delete(record)
        await session.commit()
        
        return {
            "success": True,
            "message": "Record deleted successfully"
        }
