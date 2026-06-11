# ──────────────────────────────────────────────────────────────
# app/schemas/health.py
# Pydantic v2 schemas for health profile endpoints.
# ──────────────────────────────────────────────────────────────

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Re-use the same enums defined in the ORM model to keep a
# single source of truth — no duplication of enum values.
from app.models.health_profile import (
    ActivityLevel,
    DietaryPreference,
    FitnessGoal,
    Gender,
    StressLevel,
    WorkoutPreference,
)


# ── Create Request ─────────────────────────────────────────────

class HealthProfileCreateRequest(BaseModel):
    """
    Payload for POST /api/v1/health/profile
    Submitted at the end of the onboarding assessment wizard.
    All fields are optional so users can save partial progress.
    """

    # ── Personal ───────────────────────────────────────────────
    age: Optional[int] = Field(
        default=None,
        ge=10,
        le=120,
        description="Age in years (10–120)",
        examples=[28],
    )

    gender: Optional[Gender] = Field(
        default=None,
        examples=[Gender.male],
    )

    height_cm: Optional[float] = Field(
        default=None,
        ge=50.0,
        le=300.0,
        description="Height in centimetres (50–300)",
        examples=[175.0],
    )

    weight_kg: Optional[float] = Field(
        default=None,
        ge=20.0,
        le=500.0,
        description="Current body weight in kilograms (20–500)",
        examples=[72.5],
    )

    target_weight_kg: Optional[float] = Field(
        default=None,
        ge=20.0,
        le=500.0,
        description="Goal body weight in kilograms (20–500)",
        examples=[68.0],
    )

    # ── Fitness ────────────────────────────────────────────────
    fitness_goal: Optional[FitnessGoal] = Field(
        default=None,
        examples=[FitnessGoal.weight_loss],
    )

    activity_level: Optional[ActivityLevel] = Field(
        default=None,
        examples=[ActivityLevel.moderate],
    )

    workout_preference: Optional[WorkoutPreference] = Field(
        default=None,
        examples=[WorkoutPreference.home],
    )

    available_workout_days: Optional[int] = Field(
        default=None,
        ge=1,
        le=7,
        description="Number of days per week available for exercise (1–7)",
        examples=[4],
    )

    available_workout_minutes: Optional[int] = Field(
        default=None,
        ge=5,
        le=300,
        description="Minutes available per workout session (5–300)",
        examples=[45],
    )

    # ── Health & Medical ───────────────────────────────────────
    medical_conditions: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Comma-separated or free-text medical conditions",
        examples=["Type 2 diabetes, hypertension"],
    )

    injuries: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Current or past injuries relevant to workout planning",
        examples=["Left knee ligament tear (recovered)"],
    )

    allergies: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Food or environmental allergies",
        examples=["Peanuts, shellfish"],
    )

    # ── Nutrition ──────────────────────────────────────────────
    dietary_preferences: Optional[DietaryPreference] = Field(
        default=None,
        examples=[DietaryPreference.vegetarian],
    )

    food_restrictions: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Additional restrictions beyond dietary preference",
        examples=["No gluten, no dairy"],
    )

    daily_water_intake_liters: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=20.0,
        description="Current average daily water intake in litres",
        examples=[2.0],
    )

    # ── Lifestyle ──────────────────────────────────────────────
    sleep_hours: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=24.0,
        description="Average nightly sleep in hours (0–24)",
        examples=[7.5],
    )

    stress_level: Optional[StressLevel] = Field(
        default=None,
        examples=[StressLevel.moderate],
    )

    occupation: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Job/occupation (used to estimate daily activity level)",
        examples=["Software Engineer"],
    )

    # ── Cross-field validation ─────────────────────────────────
    @model_validator(mode="after")
    def validate_weight_targets(self) -> "HealthProfileCreateRequest":
        """Target weight must be a realistic delta from current weight."""
        if self.weight_kg and self.target_weight_kg:
            delta = abs(self.weight_kg - self.target_weight_kg)
            if delta > 200:
                raise ValueError(
                    "Target weight differs from current weight by more than 200 kg. "
                    "Please enter a realistic goal."
                )
        return self


# ── Update Request ─────────────────────────────────────────────

class HealthProfileUpdateRequest(BaseModel):
    """
    Payload for PATCH /api/v1/health/profile
    All fields are optional — only provided fields are updated (partial update).
    Uses the same validation rules as HealthProfileCreateRequest.
    """

    age: Optional[int] = Field(default=None, ge=10, le=120)
    gender: Optional[Gender] = None
    height_cm: Optional[float] = Field(default=None, ge=50.0, le=300.0)
    weight_kg: Optional[float] = Field(default=None, ge=20.0, le=500.0)
    target_weight_kg: Optional[float] = Field(default=None, ge=20.0, le=500.0)
    fitness_goal: Optional[FitnessGoal] = None
    activity_level: Optional[ActivityLevel] = None
    workout_preference: Optional[WorkoutPreference] = None
    available_workout_days: Optional[int] = Field(default=None, ge=1, le=7)
    available_workout_minutes: Optional[int] = Field(default=None, ge=5, le=300)
    medical_conditions: Optional[str] = Field(default=None, max_length=1000)
    injuries: Optional[str] = Field(default=None, max_length=1000)
    allergies: Optional[str] = Field(default=None, max_length=500)
    dietary_preferences: Optional[DietaryPreference] = None
    food_restrictions: Optional[str] = Field(default=None, max_length=500)
    daily_water_intake_liters: Optional[float] = Field(default=None, ge=0.0, le=20.0)
    sleep_hours: Optional[float] = Field(default=None, ge=0.0, le=24.0)
    stress_level: Optional[StressLevel] = None
    occupation: Optional[str] = Field(default=None, max_length=150)

    @model_validator(mode="after")
    def validate_weight_targets(self) -> "HealthProfileUpdateRequest":
        if self.weight_kg and self.target_weight_kg:
            delta = abs(self.weight_kg - self.target_weight_kg)
            if delta > 200:
                raise ValueError(
                    "Target weight differs from current weight by more than 200 kg."
                )
        return self


# ── Response ───────────────────────────────────────────────────

class HealthProfileResponse(BaseModel):
    """
    Returned by GET and POST /api/v1/health/profile.
    Maps directly from the HealthProfile ORM object.
    Includes computed fields (bmi, bmi_category, is_assessment_complete).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    # Personal
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None   # Computed property from ORM model

    # Fitness
    fitness_goal: Optional[FitnessGoal] = None
    activity_level: Optional[ActivityLevel] = None
    workout_preference: Optional[WorkoutPreference] = None
    available_workout_days: Optional[int] = None
    available_workout_minutes: Optional[int] = None

    # Health
    medical_conditions: Optional[str] = None
    injuries: Optional[str] = None
    allergies: Optional[str] = None

    # Nutrition
    dietary_preferences: Optional[DietaryPreference] = None
    food_restrictions: Optional[str] = None
    daily_water_intake_liters: Optional[float] = None

    # Lifestyle
    sleep_hours: Optional[float] = None
    stress_level: Optional[StressLevel] = None
    occupation: Optional[str] = None

    # State
    is_assessment_complete: bool = False

    # Timestamps
    created_at: datetime
    updated_at: datetime
