"""
User and JWT Token SQLAlchemy Models
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models_sql.base import Base

class User(Base):
    __tablename__ = "users"
    
    # Primary Key
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Line Authentication
    line_id = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255))
    picture_url = Column(Text)
    
    # User Information
    fname = Column(String(255), nullable=False)
    lname = Column(String(255), nullable=False)
    gender = Column(String(20))
    role = Column(String(50), default='owner')
    is_registered = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Contact Information
    phone = Column(String(20))
    email = Column(String(255), index=True)
    
    # Address Information
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    subdistrict = Column(String(100))
    district = Column(String(100))
    province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default='Thailand')
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    jwt_token = relationship("JWTToken", back_populates="user", uselist=False, cascade="all, delete-orphan")
    pets = relationship("Pet", back_populates="user", cascade="all, delete-orphan")
    medicines = relationship("Medicine", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")


class JWTToken(Base):
    __tablename__ = "jwt_tokens"
    
    # Primary Key
    token_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Key (1:1 with User)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Token Information
    access_token = Column(Text, nullable=False)
    key_id = Column(String(255))
    token_type = Column(String(50), default='Bearer')
    expires_at = Column(TIMESTAMP, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    user = relationship("User", back_populates="jwt_token")
