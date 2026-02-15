"""
User Service (SQL Version)
Handles user profile, pet management, and basic CRUD operations
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models_sql.user_model import User
from app.models_sql.pet_model import Pet, PetRecord
from app.models_sql.medicine_model import Medicine
from app.models_sql.appointment_model import Appointment
from app.schemas.register_schema import OwnerRegister, PetRegister
from app.schemas.pet_schema import PetUpdateSchema


async def register_owner(session: AsyncSession, user_id: int, owner_data: OwnerRegister) -> bool:
    """
    Update user profile with registration data
    
    Args:
        session: Database session
        user_id: User ID
        owner_data: Owner registration data
    
    Returns:
        True if successful, False otherwise
    """
    result = await session.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(
            fname=owner_data.first_name,
            lname=owner_data.last_name,
            phone=owner_data.phone,
            email=owner_data.email,
            address_line1=owner_data.address_line1,
            address_line2=owner_data.address_line2,
            subdistrict=owner_data.subdistrict,
            district=owner_data.district,
            province=owner_data.province,
            postal_code=owner_data.postal_code,
            is_registered=True,
        )
    )
    await session.commit()
    return result.rowcount > 0


async def get_user_profile(session: AsyncSession, user_id: int) -> Optional[Dict]:
    """
    Get user profile with pets
    
    Args:
        session: Database session
        user_id: User ID
    
    Returns:
        User profile dict with pets list
    """
    result = await session.execute(
        select(User)
        .options(selectinload(User.pets))
        .where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    # Convert to dict
    profile = {
        "user_id": user.user_id,
        "line_id": user.line_id,
        "display_name": user.display_name,
        "picture_url": user.picture_url,
        "fname": user.fname,
        "lname": user.lname,
        "gender": user.gender,
        "phone": user.phone,
        "email": user.email,
        "address_line1": user.address_line1,
        "address_line2": user.address_line2,
        "subdistrict": user.subdistrict,
        "district": user.district,
        "province": user.province,
        "postal_code": user.postal_code,
        "country": user.country,
        "is_registered": user.is_registered,
        "pets": [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "breed": pet.breed,
                "profile_image": pet.profile_image,
            }
            for pet in user.pets if not pet.is_deleted
        ]
    }
    
    return profile


async def update_user_profile(session: AsyncSession, user_id: int, update_data: Dict) -> bool:
    """
    Update user profile fields
    
    Args:
        session: Database session
        user_id: User ID
        update_data: Dict of fields to update
    
    Returns:
        True if successful, False otherwise
    """
    # Filter out None values
    filtered_data = {k: v for k, v in update_data.items() if v is not None}
    
    if not filtered_data:
        return False
    
    result = await session.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(**filtered_data)
    )
    await session.commit()
    return result.rowcount > 0


# ==================== PET MANAGEMENT ====================

async def get_pets_by_owner(session: AsyncSession, user_id: int) -> List[Dict]:
    """
    Get all pets owned by user
    
    Args:
        session: Database session
        user_id: User ID (owner)
    
    Returns:
        List of pet dicts
    """
    result = await session.execute(
        select(Pet)
        .where(and_(Pet.user_id == user_id, Pet.is_deleted == False))
        .order_by(Pet.created_at.desc())
    )
    pets = result.scalars().all()
    
    return [
        {
            "pet_id": pet.pet_id,
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "color": pet.color,
            "gender": pet.gender,
            "birth_date": pet.birth_date.isoformat() if pet.birth_date else None,
            "weight_kg": float(pet.weight_kg) if pet.weight_kg else None,
            "allergies": pet.allergies,
            "infecund": pet.infecund,
            "in_medical": pet.in_medical,
            "profile_image": pet.profile_image,
            "is_verified": pet.is_verified,
            "created_at": pet.created_at.isoformat() if pet.created_at else None,
        }
        for pet in pets
    ]


async def register_new_pet(session: AsyncSession, user_id: int, pet_data: PetRegister) -> int:
    """
    Register new pet for user
    
    Args:
        session: Database session
        user_id: Owner user ID
        pet_data: Pet registration data
    
    Returns:
        New pet ID
    """
    new_pet = Pet(
        user_id=user_id,
        name=pet_data.name,
        species=pet_data.species,
        breed=pet_data.breed,
        color=pet_data.color,
        gender=pet_data.gender,
        birth_date=pet_data.birth_date,
        weight_kg=pet_data.weight_kg,
        infecund=pet_data.infecund,
        in_medical=pet_data.in_medical,
        profile_image=pet_data.profile_image,
        is_verified=False,
        is_deleted=False,
    )
    
    session.add(new_pet)
    await session.commit()
    await session.refresh(new_pet)
    
    return new_pet.pet_id


async def get_pet_by_id(session: AsyncSession, pet_id: int) -> Optional[Dict]:
    """
    Get pet details by ID
    
    Args:
        session: Database session
        pet_id: Pet ID
    
    Returns:
        Pet dict or None
    """
    result = await session.execute(
        select(Pet).where(and_(Pet.pet_id == pet_id, Pet.is_deleted == False))
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        return None
    
    return {
        "pet_id": pet.pet_id,
        "user_id": pet.user_id,
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "color": pet.color,
        "gender": pet.gender,
        "birth_date": pet.birth_date.isoformat() if pet.birth_date else None,
        "weight_kg": float(pet.weight_kg) if pet.weight_kg else None,
        "allergies": pet.allergies,
        "infecund": pet.infecund,
        "in_medical": pet.in_medical,
        "profile_image": pet.profile_image,
        "is_verified": pet.is_verified,
        "created_at": pet.created_at.isoformat() if pet.created_at else None,
    }


async def update_pet_info(session: AsyncSession, pet_id: int, data: PetUpdateSchema) -> bool:
    """
    Update pet information
    
    Args:
        session: Database session
        pet_id: Pet ID
        data: Update schema
    
    Returns:
        True if successful, False otherwise
    """
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    if not update_data:
        return False
    
    result = await session.execute(
        update(Pet)
        .where(Pet.pet_id == pet_id)
        .values(**update_data)
    )
    await session.commit()
    return result.rowcount > 0


async def delete_pet(session: AsyncSession, pet_id: int) -> bool:
    """
    Soft delete pet
    
    Args:
        session: Database session
        pet_id: Pet ID
    
    Returns:
        True if successful, False otherwise
    """
    result = await session.execute(
        update(Pet)
        .where(Pet.pet_id == pet_id)
        .values(is_deleted=True)
    )
    await session.commit()
    return result.rowcount > 0


# ==================== PET RECORDS ====================

async def add_pet_record(session: AsyncSession, pet_id: int, note: str, images: Optional[List[str]] = None) -> int:
    """
    Add pet health/behavior record
    
    Args:
        session: Database session
        pet_id: Pet ID
        note: Record note/description
        images: Optional list of image URLs
    
    Returns:
        New record ID
    """
    new_record = PetRecord(
        pet_id=pet_id,
        note=note,
        images=images or [],
    )
    
    session.add(new_record)
    await session.commit()
    await session.refresh(new_record)
    
    return new_record.record_id


async def get_pet_records(session: AsyncSession, pet_id: int) -> List[Dict]:
    """
    Get all records for a pet
    
    Args:
        session: Database session
        pet_id: Pet ID
    
    Returns:
        List of record dicts
    """
    result = await session.execute(
        select(PetRecord)
        .where(PetRecord.pet_id == pet_id)
        .order_by(PetRecord.created_at.desc())
    )
    records = result.scalars().all()
    
    return [
        {
            "record_id": record.record_id,
            "pet_id": record.pet_id,
            "note": record.note,
            "images": record.images,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        for record in records
    ]


# ==================== DASHBOARD DATA ====================

async def get_dashboard_data(session: AsyncSession, user_id: int) -> Dict:
    """
    Get dashboard summary data for user
    
    Args:
        session: Database session
        user_id: User ID
    
    Returns:
        Dashboard data dict
    """
    # Get pets
    pets_result = await session.execute(
        select(Pet)
        .where(and_(Pet.user_id == user_id, Pet.is_deleted == False))
        .limit(10)
    )
    pets = pets_result.scalars().all()
    
    # Get upcoming appointments
    appointments_result = await session.execute(
        select(Appointment)
        .where(and_(
            Appointment.user_id == user_id,
            Appointment.status == 'Upcoming',
            Appointment.is_deleted == False
        ))
        .order_by(Appointment.appointment_date.asc())
        .limit(5)
    )
    appointments = appointments_result.scalars().all()
    
    # Get active medications
    medications_result = await session.execute(
        select(Medicine)
        .where(and_(
            Medicine.user_id == user_id,
            Medicine.status == 'TAKE',
            Medicine.is_deleted == False
        ))
        .limit(5)
    )
    medications = medications_result.scalars().all()
    
    return {
        "my_pets": [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "profile_image": pet.profile_image,
            }
            for pet in pets
        ],
        "upcoming_appointments": [
            {
                "appointment_id": appt.appointment_id,
                "pet_id": appt.pet_id,
                "location": appt.location,
                "appointment_date": appt.appointment_date.isoformat() if appt.appointment_date else None,
            }
            for appt in appointments
        ],
        "active_medications": [
            {
                "medicine_id": med.medicine_id,
                "pet_id": med.pet_id,
                "name": med.name,
                "dosage": med.dosage,
                "frequency": med.frequency,
            }
            for med in medications
        ]
    }
