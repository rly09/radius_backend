"""
Services Router — CRUD + Smart Search endpoints.

GET  /services       — Search services by location & category (decision-ranked)
POST /services       — Add a new service
GET  /services/{id}  — Get service details with reviews
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import httpx
import hashlib
import random
from datetime import time

from database import get_db
from models.service import Service, Review
from schemas.service import (
    ServiceCreate, ServiceOut, ServiceDetail,
    ReviewOut, DecisionResult, SmartSearchResponse,
    CrowdUpdateInput
)
from services.decision_engine import DecisionEngine

# ── Google Maps API Key ──────────────────────────────────
GOOGLE_MAPS_API_KEY = "AIzaSyAjKAdUcx2zDuGUhHu0cEK-YcNELj3-O84"

router = APIRouter(prefix="/services", tags=["Services"])
engine = DecisionEngine()

def hash_place_id(place_id: str) -> int:
    """Generate a deterministic positive integer ID from Google place_id (7 hex chars max)."""
    return int(hashlib.md5(place_id.encode()).hexdigest()[:7], 16)

def get_google_place_type(category: str) -> str:
    mapping = {
        "hospital": "hospital",
        "food": "restaurant",
        "repair": "car_repair",
        "grocery": "supermarket",
        "pharmacy": "pharmacy",
        "atm": "atm",
        "gas_station": "gas_station",
        "police": "police"
    }
    return mapping.get(category)

@router.get("", response_model=SmartSearchResponse)
async def search_services(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    category: Optional[str] = Query(None, description="Service category filter"),
    db: Session = Depends(get_db),
):
    """
    Search for nearby services via Google Places API with smart decision-based ranking.
    Returns categorized results: best_option, fastest, top_rated.
    """
    cat = (category or "hospital").lower()
    place_type = get_google_place_type(cat)
    
    # ── Fetch from Google Places API ──────────────────────────────────
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 5000,
        "key": GOOGLE_MAPS_API_KEY,
    }
    
    if place_type:
        params["type"] = place_type
    else:
        params["keyword"] = cat
    
    services = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            data = resp.json()
            
            if data.get("status") == "OK":
                for item in data.get("results", [])[:15]: # Limit to 15 results
                    place_hash = hash_place_id(item["place_id"])
                    
                    # Check if already cached in DB
                    existing = db.query(Service).filter(Service.id == place_hash).first()
                    if existing:
                        services.append(existing)
                    else:
                        # Create and cache Service object
                        svc = Service(
                            id=place_hash,
                            name=item.get("name", "Unknown Place"),
                            category=cat,
                            latitude=item["geometry"]["location"]["lat"],
                            longitude=item["geometry"]["location"]["lng"],
                            address=item.get("vicinity", "Address not available"),
                            phone="", # Nearby search doesn't return phone
                            rating=item.get("rating", 0.0),
                            open_time=time(0, 0),   # Dummy open 24/7
                            close_time=time(23, 59), # Dummy open 24/7
                            is_emergency=(cat == "hospital"),
                            crowd_level="medium",
                            wait_time=random.randint(5, 15)
                        )
                        db.add(svc)
                        db.commit()
                        db.refresh(svc)
                        services.append(svc)
    except Exception as e:
        print(f"Places API Error: {e}")
        pass # Fallback to DB if Places fails

    if not services:
        # Fallback to DB query if Places API failed or returned nothing
        query = db.query(Service)
        if category:
            query = query.filter(Service.category == cat)
        services = query.all()

    if not services:
        return SmartSearchResponse(
            category=cat,
            total_found=0,
            decisions=[],
            all_services=[]
        )

    # Run decision engine
    decisions_raw, all_ranked = engine.get_decision_results(services, latitude, longitude)

    # Build decision results
    decisions = []
    for d in decisions_raw:
        svc = d["service"]["service"]
        decisions.append(DecisionResult(
            label=d["label"],
            emoji=d["emoji"],
            description=d["description"],
            service=ServiceOut(
                id=svc.id,
                name=svc.name,
                category=svc.category,
                latitude=svc.latitude,
                longitude=svc.longitude,
                address=svc.address,
                phone=svc.phone,
                rating=float(svc.rating),
                open_time=svc.open_time,
                close_time=svc.close_time,
                is_emergency=svc.is_emergency,
                crowd_level=svc.crowd_level,
                wait_time=svc.wait_time,
                is_open=d["service"]["is_open"],
                distance_km=d["service"]["distance_km"],
                score=d["service"]["score"],
            )
        ))

    # Build all services list
    all_services = []
    for r in all_ranked:
        svc = r["service"]
        all_services.append(ServiceOut(
            id=svc.id,
            name=svc.name,
            category=svc.category,
            latitude=svc.latitude,
            longitude=svc.longitude,
            address=svc.address,
            phone=svc.phone,
            rating=float(svc.rating),
            open_time=svc.open_time,
            close_time=svc.close_time,
            is_emergency=svc.is_emergency,
            crowd_level=svc.crowd_level,
            wait_time=svc.wait_time,
            is_open=r["is_open"],
            distance_km=r["distance_km"],
            score=r["score"],
        ))

    return SmartSearchResponse(
        category=category or "all",
        total_found=len(all_services),
        decisions=decisions,
        all_services=all_services,
    )


@router.post("", response_model=ServiceOut, status_code=201)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
):
    """Add a new service to the database."""
    service = Service(**service_data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)

    return ServiceOut(
        id=service.id,
        name=service.name,
        category=service.category,
        latitude=service.latitude,
        longitude=service.longitude,
        address=service.address,
        phone=service.phone,
        rating=float(service.rating),
        open_time=service.open_time,
        close_time=service.close_time,
        is_emergency=service.is_emergency,
        is_open=True,
        distance_km=0.0,
        score=0.0,
    )


@router.get("/{service_id}", response_model=ServiceDetail)
def get_service_detail(
    service_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed information about a service, including reviews."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    reviews = [
        ReviewOut(
            id=r.id,
            service_id=r.service_id,
            rating=float(r.rating),
            comment=r.comment,
            created_at=r.created_at,
        )
        for r in service.reviews
    ]

    return ServiceDetail(
        id=service.id,
        name=service.name,
        category=service.category,
        latitude=service.latitude,
        longitude=service.longitude,
        address=service.address,
        phone=service.phone,
        rating=float(service.rating),
        open_time=service.open_time,
        close_time=service.close_time,
        is_emergency=service.is_emergency,
        crowd_level=service.crowd_level,
        wait_time=service.wait_time,
        is_open=DecisionEngine.is_service_open(service),
        reviews=reviews,
    )

@router.post("/update-crowd", response_model=ServiceDetail)
def update_crowd(
    data: CrowdUpdateInput,
    db: Session = Depends(get_db)
):
    """Update the crowd level and wait time for a service."""
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
        
    service.crowd_level = data.crowd_level.lower()
    service.wait_time = data.wait_time
    db.commit()
    db.refresh(service)
    
    return get_service_detail(service_id=service.id, db=db)
