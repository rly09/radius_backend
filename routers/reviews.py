"""
Reviews Router — Add reviews to services.

POST /reviews — Add a review for a service.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.service import Service, Review
from schemas.service import ReviewCreate, ReviewOut

router = APIRouter(tags=["Reviews"])


@router.post("/reviews", response_model=ReviewOut, status_code=201)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
):
    """Add a review for a service and update the service's average rating."""
    # Check service exists
    service = db.query(Service).filter(Service.id == review_data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Create review
    review = Review(
        service_id=review_data.service_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(review)
    db.commit()

    # Update service average rating
    all_reviews = db.query(Review).filter(Review.service_id == review_data.service_id).all()
    if all_reviews:
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        service.rating = round(avg_rating, 1)
        db.commit()

    db.refresh(review)

    return ReviewOut(
        id=review.id,
        service_id=review.service_id,
        rating=float(review.rating),
        comment=review.comment,
        created_at=review.created_at,
    )
