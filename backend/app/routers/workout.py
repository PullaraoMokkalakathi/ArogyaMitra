# ──────────────────────────────────────────────────────────────
# app/routers/workout.py
# Workout plan generation endpoints.
# ──────────────────────────────────────────────────────────────

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.health_profile import HealthProfile
from app.models.user import User
from app.services.workout_generator import generate_workout_plan, to_dict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workout", tags=["Workout"])


# ── GET /plan ──────────────────────────────────────────────────────

@router.get(
    "/plan",
    status_code=status.HTTP_200_OK,
    summary="Get personalized workout plan",
    responses={
        404: {"description": "Health profile not found"},
    },
)
def get_workout_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Generate a personalized workout plan for the authenticated user
    based on their health profile data.
    """
    health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()

    if not health_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found. Please complete onboarding first.",
        )

    if not health_profile.height_cm or not health_profile.weight_kg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Height and weight required for workout plan generation.",
        )

    workout_plan = generate_workout_plan(
        age=health_profile.age or 25,
        gender=health_profile.gender.value if health_profile.gender else "other",
        height_cm=health_profile.height_cm,
        weight_kg=health_profile.weight_kg,
        fitness_goal=health_profile.fitness_goal.value if health_profile.fitness_goal else "maintenance",
        activity_level=health_profile.activity_level.value if health_profile.activity_level else "moderate",
    )

    logger.info(f"Workout plan generated: user_id={current_user.id}")

    return to_dict(workout_plan)