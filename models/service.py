"""SQLAlchemy ORM models for services and reviews."""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    Time, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Service(Base):
    """Model representing an essential service."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default="other")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=False)
    phone = Column(String(20), nullable=False)
    rating = Column(Float, default=0.0)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
    is_emergency = Column(Boolean, default=False)
    crowd_level = Column(
        Enum("low", "medium", "high", name="crowd_level_enum"),
        default="medium"
    )
    wait_time = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    reviews = relationship("Review", back_populates="service", cascade="all, delete-orphan")


class Review(Base):
    """Model representing a user review for a service."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    service = relationship("Service", back_populates="reviews")
