# ──────────────────────────────────────────────────────────────
# app/routers/health.py
# Health profile management endpoints.
# ──────────────────────────────────────────────────────────────

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.health_profile import HealthProfile
from app.models.user import User
from app.schemas.health import (
    HealthProfileCreateRequest,
    HealthProfileResponse,
    HealthProfileUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


# ── POST /profile ──────────────────────────────────────────────

@router.post(
    "/profile",
    response_model=HealthProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new health profile",
    responses={
        400: {"description": "Profile already exists"},
        422: {"description": "Validation error"},
    },
)
def create_profile(
    payload: HealthProfileCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HealthProfileResponse:
    """
    Create a new health profile for the authenticated user.
    Each user can only have one active health profile.
    """
    # ── 1. Check for existing profile ──────────────────────────
    existing_profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A health profile already exists for this user. Use PUT to update it.",
        )

    # ── 2. Create profile ──────────────────────────────────────
    profile_data = payload.model_dump(exclude_unset=True)
    health_profile = HealthProfile(
        user_id=current_user.id,
        is_assessment_complete=True,  # Mark as complete upon creation
        **profile_data
    )

    # ── 3. Persist and return ──────────────────────────────────
    try:
        # Pre-compute BMI if height and weight are provided
        health_profile.compute_bmi()
        
        db.add(health_profile)
        db.commit()
        db.refresh(health_profile)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create health profile due to database integrity error.",
        )

    logger.info(f"Health profile created: user_id={current_user.id} profile_id={health_profile.id}")

    return HealthProfileResponse.model_validate(health_profile)


# ── GET /profile ───────────────────────────────────────────────

@router.get(
    "/profile",
    response_model=HealthProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current user's health profile",
    responses={
        404: {"description": "Health profile not found"},
    },
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HealthProfileResponse:
    """
    Retrieve the health profile for the currently authenticated user.
    """
    health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()

    if not health_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found for the current user.",
        )

    return HealthProfileResponse.model_validate(health_profile)


# ── PUT /profile ───────────────────────────────────────────────

@router.put(
    "/profile",
    response_model=HealthProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the current user's health profile",
    responses={
        404: {"description": "Health profile not found"},
        422: {"description": "Validation error"},
    },
)
def update_profile(
    payload: HealthProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HealthProfileResponse:
    """
    Update the health profile for the currently authenticated user.
    Supports partial updates — only provided fields will be modified.
    """
    # ── 1. Lookup existing profile ─────────────────────────────
    health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()

    if not health_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found. Please create one first.",
        )

    # ── 2. Apply partial updates ───────────────────────────────
    update_data = payload.model_dump(exclude_unset=True)
    
    if not update_data:
        # Nothing to update, return the existing profile
        return HealthProfileResponse.model_validate(health_profile)

    for key, value in update_data.items():
        setattr(health_profile, key, value)

    # Re-compute BMI if height or weight were modified
    if "height_cm" in update_data or "weight_kg" in update_data:
        health_profile.compute_bmi()

    # ── 3. Persist and return ──────────────────────────────────
    try:
        db.commit()
        db.refresh(health_profile)
    except Exception as exc:
        db.rollback()
        logger.error(f"Error updating health profile for user_id={current_user.id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the health profile.",
        )

    logger.info(f"Health profile updated: user_id={current_user.id}")

    return HealthProfileResponse.model_validate(health_profile)
