"""
Pet and Pet Records SQLAlchemy Models
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP, ForeignKey, Date, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models_sql.base import Base

class Pet(Base):
    __tablename__ = "pets"
    
    # Primary Key
    pet_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Key
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Pet Information
    name = Column(String(255), nullable=False, index=True)
    species = Column(String(100))
    breed = Column(String(255))
    color = Column(String(100))
    gender = Column(String(20))
    birth_date = Column(Date)
    weight_kg = Column(DECIMAL(6, 2))
    
    # Medical Information
    allergies = Column(JSON, comment='Array of allergy strings: ["penicillin", "chicken"]')
    infecund = Column(Boolean, default=False, comment='ทำหมัน/ตอนแล้ว')
    
    # Media
    profile_image = Column(Text)
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    user = relationship("User", back_populates="pets")
    medicines = relationship("Medicine", back_populates="pet", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="pet", cascade="all, delete-orphan")
    records = relationship("PetRecord", back_populates="pet", cascade="all, delete-orphan")


class PetRecord(Base):
    __tablename__ = "pets_records"
    
    # Primary Key
    record_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Key
    pet_id = Column(BigInteger, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Record Information
    note = Column(Text, nullable=False)
    images = Column(JSON, comment='Array of image URLs')
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    pet = relationship("Pet", back_populates="records")
