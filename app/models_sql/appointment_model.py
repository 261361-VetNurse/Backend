"""
Appointment and Appointment Notification SQLAlchemy Models
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models_sql.base import Base

class Appointment(Base):
    __tablename__ = "appointments"
    
    # Primary Key
    appointment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys (user_id is denormalized, auto-populated by trigger)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True,
                     comment='Denormalized from pets.user_id for performance')
    pet_id = Column(BigInteger, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Appointment Information
    location = Column(String(500), nullable=False)
    appointment_date = Column(TIMESTAMP, nullable=False, index=True)
    note = Column(Text)
    status = Column(String(50), default='Upcoming', index=True)
    
    # Status
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('Upcoming', 'Completed', 'Canceled')", name='ck_appointment_status'),
    )
    
    # Relationships
    user = relationship("User", back_populates="appointments")
    pet = relationship("Pet", back_populates="appointments")
    notifications = relationship("AppointmentNotification", back_populates="appointment", cascade="all, delete-orphan")


class AppointmentNotification(Base):
    __tablename__ = "appointments_notification"
    
    # Primary Key
    notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys (user_id, pet_id are denormalized for fast queries)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True,
                     comment='For fast user-based queries')
    pet_id = Column(BigInteger, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False, index=True,
                    comment='For fast pet-based queries')
    appointment_id = Column(BigInteger, ForeignKey('appointments.appointment_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Notification Information
    title = Column(String(500), nullable=False, comment='e.g., "Reminder: Appointment at ABC Clinic for Lucky"')
    notification_at = Column(TIMESTAMP, nullable=False, index=True, comment='Created immediately after appointment')
    
    # Status Tracking
    sending_status = Column(String(50), default='not_sent', index=True)
    status = Column(String(50), default='pending')
    sending_count = Column(BigInteger, default=0)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("sending_status IN ('not_sent', 'sent', 'failed')", name='ck_appt_notif_sending_status'),
        CheckConstraint("status IN ('pending', 'sent', 'failed', 'canceled')", name='ck_appt_notif_status'),
    )
    
    # Relationships
    appointment = relationship("Appointment", back_populates="notifications")
