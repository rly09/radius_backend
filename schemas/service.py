"""Pydantic schemas for request validation and response serialization."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import time, datetime


# ── Service Schemas ──────────────────────────────────────

class ServiceBase(BaseModel):
    """Base schema with common service fields."""
    name: str
    category: str
    latitude: float
    longitude: float
    address: str
    phone: str
    rating: float = 0.0
    open_time: time
    close_time: time
    is_emergency: bool = False


class ServiceCreate(ServiceBase):
    """Schema for creating a new service."""
    pass


class ServiceOut(BaseModel):
    """Schema for service in list/search results."""
    id: int
    name: str
    category: str
    latitude: float
    longitude: float
    address: str
    phone: str
    rating: float
    open_time: time
    close_time: time
    is_emergency: bool
    crowd_level: str = "medium"
    wait_time: int = 10
    is_open: bool = True
    distance_km: float = 0.0
    duration_minutes: float = 0.0
    score: float = 0.0

    model_config = {"from_attributes": True}


class ReviewOut(BaseModel):
    """Schema for review output."""
    id: int
    service_id: int
    rating: float
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ServiceDetail(ServiceOut):
    """Schema for detailed service view with reviews."""
    reviews: List[ReviewOut] = []

    model_config = {"from_attributes": True}


# ── Review Schemas ───────────────────────────────────────

class ReviewBase(BaseModel):
    """Base review schema."""
    rating: float
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Schema for creating a review."""
    service_id: int


class CrowdUpdateInput(BaseModel):
    """Schema for updating crowd level and wait time."""
    service_id: int
    crowd_level: str
    wait_time: int


# ── Decision Engine Response ─────────────────────────────

class DecisionResult(BaseModel):
    """A single decision-ranked service result."""
    label: str          # e.g. "best_option", "fastest", "top_rated"
    emoji: str          # e.g. "🥇", "⚡", "⭐"
    description: str    # e.g. "Best Overall Option"
    service: ServiceOut


class SmartSearchResponse(BaseModel):
    """Response containing decision-ranked results."""
    category: str
    total_found: int
    decisions: List[DecisionResult]
    all_services: List[ServiceOut]
