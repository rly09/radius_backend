"""
Emergency Router — Instant nearest hospital lookup.

GET /emergency — Returns the nearest hospital based on user coordinates.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.service import Service
from schemas.service import ServiceOut
from services.decision_engine import DecisionEngine

router = APIRouter(tags=["Emergency"])
engine = DecisionEngine()


import httpx
import random
from datetime import time
from routers.services import hash_place_id, GOOGLE_MAPS_API_KEY

@router.get("/emergency", response_model=ServiceOut)
async def get_emergency_service(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    db: Session = Depends(get_db),
):
    """
    🚨 Emergency Mode — Returns the nearest hospital instantly.
    Always includes all hospitals regardless of open/closed status.
    """
    hospitals = []
    
    # ── Fetch from Google Places API ──────────────────────────────────
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 5000,
        "type": "hospital",
        "key": GOOGLE_MAPS_API_KEY,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            data = resp.json()
            
            if data.get("status") == "OK":
                for item in data.get("results", [])[:15]:
                    place_hash = hash_place_id(item["place_id"])
                    
                    # Check if already cached in DB
                    existing = db.query(Service).filter(Service.id == place_hash).first()
                    if existing:
                        hospitals.append(existing)
                    else:
                        svc = Service(
                            id=place_hash,
                            name=item.get("name", "Unknown Hospital"),
                            category="hospital",
                            latitude=item["geometry"]["location"]["lat"],
                            longitude=item["geometry"]["location"]["lng"],
                            address=item.get("vicinity", "Address not available"),
                            phone="",
                            rating=item.get("rating", 0.0),
                            open_time=time(0, 0),
                            close_time=time(23, 59),
                            is_emergency=True,
                            crowd_level="medium",
                            wait_time=random.randint(5, 15)
                        )
                        db.add(svc)
                        db.commit()
                        db.refresh(svc)
                        hospitals.append(svc)
    except Exception as e:
        print(f"Places API Error (Emergency): {e}")
        pass

    # ── Fallback to DB if Places API fails ────────────────────────────
    if not hospitals:
        hospitals = db.query(Service).filter(
            Service.category == "hospital",
            Service.is_emergency == True
        ).all()

    if not hospitals:
        # Fallback: any hospital
        hospitals = db.query(Service).filter(Service.category == "hospital").all()

    if not hospitals:
        return ServiceOut(
            id=0, name="No hospitals found", category="hospital",
            latitude=0, longitude=0, address="N/A", phone="N/A",
            rating=0, open_time="00:00:00", close_time="23:59:59",
            is_emergency=True, is_open=False, distance_km=0, score=0
        )

    # Find nearest hospital by distance
    ranked = engine.rank_services(hospitals, latitude, longitude, filter_open=False)
    nearest = min(ranked, key=lambda x: x["distance_km"])
    svc = nearest["service"]

    return ServiceOut(
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
        is_open=nearest["is_open"],
        distance_km=nearest["distance_km"],
        score=nearest["score"],
    )
