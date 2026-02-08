"""
Medicine and Medicine Notification SQLAlchemy Models
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Text, TIMESTAMP, ForeignKey, Date, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models_sql.base import Base

class Medicine(Base):
    __tablename__ = "medicines"
    
    # Primary Key
    medicine_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys (user_id is denormalized, auto-populated by trigger)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True, 
                     comment='Denormalized from pets.user_id for performance')
    pet_id = Column(BigInteger, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Medicine Information
    name = Column(String(255), nullable=False)
    properties = Column(Text, comment='Medicine properties/description')
    dosage = Column(String(100), comment='e.g., "1 tablet", "5ml"')
    
    # Schedule Information
    frequency = Column(String(50), nullable=False, comment='-1=daily, 0-6=weekdays, comma-separated like "0,2,4"')
    status = Column(String(20), default='TAKE', index=True, comment='TAKE=active, STOP=stopped')
    reminder_time = Column(JSON, nullable=False, comment='Array of time strings: ["08:00", "20:00"]')
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # History & Media
    notes = Column(JSON, comment='Array of notes (max 3): ["note1", "note2", "note3"]')
    image_urls = Column(JSON, comment='Array of image URLs')
    
    # Status
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('TAKE', 'STOP')", name='ck_medicine_status'),
        CheckConstraint("start_date <= end_date", name='ck_medicine_dates'),
    )
    
    # Relationships
    user = relationship("User", back_populates="medicines")
    pet = relationship("Pet", back_populates="medicines")
    notifications = relationship("MedicineNotification", back_populates="medicine", cascade="all, delete-orphan")


class MedicineNotification(Base):
    __tablename__ = "medicines_notification"
    
    # Primary Key
    notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys (user_id, pet_id are denormalized for fast queries)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True,
                     comment='For fast user-based queries')
    pet_id = Column(BigInteger, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False, index=True,
                    comment='For fast pet-based queries')
    medicine_id = Column(BigInteger, ForeignKey('medicines.medicine_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Notification Information
    title = Column(String(500), nullable=False, comment='e.g., "Time to give Amoxicillin to Lucky"')
    notification_at = Column(TIMESTAMP, nullable=False, index=True, comment='Scheduled notification time')
    
    # Status Tracking
    sending_status = Column(String(50), default='not_sent', index=True, comment='not_sent, sent, failed')
    status = Column(String(50), default='pending', comment='pending, sent, failed, canceled')
    sending_count = Column(BigInteger, default=0, comment='Number of send attempts')
    istaken = Column(Boolean, default=False, index=True, comment='User marked as taken')
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("sending_status IN ('not_sent', 'sent', 'failed')", name='ck_med_notif_sending_status'),
        CheckConstraint("status IN ('pending', 'sent', 'failed', 'canceled')", name='ck_med_notif_status'),
    )
    
    # Relationships
    medicine = relationship("Medicine", back_populates="notifications")
