"""
Directions Router — Proxy for Google Directions API.

GET /directions — Get distance, duration, and route polyline between two points.
"""

import os
from dotenv import load_dotenv
import httpx
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

# ── Load Environment Variables ────────────────────────────
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

router = APIRouter(tags=["Directions"])


class DirectionsResponse(BaseModel):
    """Response with distance, duration, and encoded polyline."""
    distance_km: float
    distance_text: str
    duration_minutes: float
    duration_text: str
    polyline: str


@router.get("/directions", response_model=DirectionsResponse)
async def get_directions(
    origin_lat: float = Query(..., description="Origin latitude"),
    origin_lng: float = Query(..., description="Origin longitude"),
    dest_lat: float = Query(..., description="Destination latitude"),
    dest_lng: float = Query(..., description="Destination longitude"),
):
    """
    Proxy to Google Directions API.
    Returns distance (km), duration (minutes), and encoded polyline.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin_lat},{origin_lng}",
        "destination": f"{dest_lat},{dest_lng}",
        "mode": "driving",
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            data = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to reach Google Directions API")

    if data.get("status") != "OK" or not data.get("routes"):
        # Fallback: return Haversine-based estimate
        from services.decision_engine import DecisionEngine
        dist = DecisionEngine.haversine(origin_lat, origin_lng, dest_lat, dest_lng)
        est_minutes = round(dist / 30 * 60, 1)  # ~30 km/h city driving
        return DirectionsResponse(
            distance_km=round(dist, 2),
            distance_text=f"{round(dist, 1)} km",
            duration_minutes=est_minutes,
            duration_text=f"{int(est_minutes)} min",
            polyline="",
        )

    leg = data["routes"][0]["legs"][0]
    distance_m = leg["distance"]["value"]
    duration_s = leg["duration"]["value"]

    return DirectionsResponse(
        distance_km=round(distance_m / 1000, 2),
        distance_text=leg["distance"]["text"],
        duration_minutes=round(duration_s / 60, 1),
        duration_text=leg["duration"]["text"],
        polyline=data["routes"][0].get("overview_polyline", {}).get("points", ""),
    )
