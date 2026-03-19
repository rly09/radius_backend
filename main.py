"""
Smart Service Finder — FastAPI Backend

Main application entry point with CORS and router registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import services, emergency, reviews, directions

# ── App Initialization ────────────────────────────────────

app = FastAPI(
    title="Smart Service Finder",
    description="Location-aware essential service discovery with smart decision-based ranking.",
    version="1.0.0",
)

# ── CORS Middleware ───────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow Flutter web app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ─────────────────────────────────────

app.include_router(services.router)
app.include_router(emergency.router)
app.include_router(reviews.router)
app.include_router(directions.router)


# ── Root Endpoint ─────────────────────────────────────────

@app.get("/")
def root():
    """Health check / welcome endpoint."""
    return {
        "app": "Smart Service Finder",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
