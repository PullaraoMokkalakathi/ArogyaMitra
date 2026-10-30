# ──────────────────────────────────────────────────────────────
# app/models/health_profile.py
# HealthProfile ORM model — SQLAlchemy 2.0 style.
# One-to-one with User. Stores all health & wellness data.
# ──────────────────────────────────────────────────────────────

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


# ── Enums ──────────────────────────────────────────────────────

class Gender(str, enum.Enum):
    male        = "male"
    female      = "female"
    other       = "other"
    prefer_not  = "prefer_not_to_say"


class FitnessGoal(str, enum.Enum):
    weight_loss     = "weight_loss"
    muscle_gain     = "muscle_gain"
    endurance       = "endurance"
    flexibility     = "flexibility"
    general_fitness = "general_fitness"
    stress_relief   = "stress_relief"
    rehabilitation  = "rehabilitation"


class ActivityLevel(str, enum.Enum):
    sedentary   = "sedentary"       # Little or no exercise
    light       = "light"           # 1–3 days/week
    moderate    = "moderate"        # 3–5 days/week
    active      = "active"          # 6–7 days/week
    very_active = "very_active"     # Hard exercise daily


class WorkoutPreference(str, enum.Enum):
    home    = "home"
    gym     = "gym"
    outdoor = "outdoor"
    mixed   = "mixed"


class DietaryPreference(str, enum.Enum):
    vegetarian     = "vegetarian"
    vegan          = "vegan"
    non_vegetarian = "non_vegetarian"
    pescatarian    = "pescatarian"
    keto           = "keto"
    paleo          = "paleo"
    no_preference  = "no_preference"


class StressLevel(str, enum.Enum):
    low      = "low"
    moderate = "moderate"
    high     = "high"
    very_high = "very_high"


# ── HealthProfile Model ────────────────────────────────────────

class HealthProfile(Base):
    """
    Stores a user's complete health and wellness profile.
    One-to-one with User — enforced at both ORM and DB level.
    All AI personalization runs from this data.
    """

    __tablename__ = "health_profiles"

    # ── Primary Key ────────────────────────────────────────────
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    # ── Foreign Key (one-to-one with users) ────────────────────
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,    # Enforces one-to-one at the database level
        index=True,
    )

    # ── Personal Data ──────────────────────────────────────────
    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    gender: Mapped[Optional[Gender]] = mapped_column(
        Enum(Gender, name="gender", create_constraint=True),
        nullable=True,
    )

    height_cm: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    weight_kg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    target_weight_kg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ── Fitness Data ───────────────────────────────────────────
    fitness_goal: Mapped[Optional[FitnessGoal]] = mapped_column(
        Enum(FitnessGoal, name="fitnessgoa", create_constraint=True),
        nullable=True,
    )

    activity_level: Mapped[Optional[ActivityLevel]] = mapped_column(
        Enum(ActivityLevel, name="activitylevel", create_constraint=True),
        nullable=True,
    )

    workout_preference: Mapped[Optional[WorkoutPreference]] = mapped_column(
        Enum(WorkoutPreference, name="workoutpreference", create_constraint=True),
        nullable=True,
    )

    available_workout_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    available_workout_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # ── Health & Medical Data ──────────────────────────────────
    # Stored as free-text to allow flexible, multi-value entries.
    # AI agents parse and filter these during plan generation.
    medical_conditions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Comma-separated or free-text list of medical conditions",
    )

    injuries: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Current or past injuries that affect workouts",
    )

    allergies: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Food or environmental allergies",
    )

    # ── Nutrition Preferences ──────────────────────────────────
    dietary_preferences: Mapped[Optional[DietaryPreference]] = mapped_column(
        Enum(DietaryPreference, name="dietarypreference", create_constraint=True),
        nullable=True,
    )

    food_restrictions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional food restrictions beyond dietary preference",
    )

    daily_water_intake_liters: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ── Lifestyle Data ─────────────────────────────────────────
    sleep_hours: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Average nightly sleep in hours",
    )

    stress_level: Mapped[Optional[StressLevel]] = mapped_column(
        Enum(StressLevel, name="stresslevel", create_constraint=True),
        nullable=True,
    )

    occupation: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Used to estimate NEAT (non-exercise activity thermogenesis)",
    )

    # ── Computed / Cached ──────────────────────────────────────
    # BMI is stored to avoid recomputing it on every AI request.
    # Must be updated whenever height_cm or weight_kg changes.
    bmi: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Cached BMI value — recomputed on profile update",
    )

    # ── Assessment State ───────────────────────────────────────
    is_assessment_complete: Mapped[bool] = mapped_column(
        Integer,  # SQLite-compatible boolean
        nullable=False,
        default=False,
        server_default="0",
        comment="True once the user has completed the onboarding assessment",
    )

    # ── Timestamps ─────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ── Constraints & Indexes ──────────────────────────────────
    __table_args__ = (
        CheckConstraint("age IS NULL OR (age >= 10 AND age <= 120)", name="ck_health_profiles_age"),
        CheckConstraint("height_cm IS NULL OR (height_cm >= 50 AND height_cm <= 300)", name="ck_health_profiles_height"),
        CheckConstraint("weight_kg IS NULL OR (weight_kg >= 20 AND weight_kg <= 500)", name="ck_health_profiles_weight"),
        CheckConstraint("sleep_hours IS NULL OR (sleep_hours >= 0 AND sleep_hours <= 24)", name="ck_health_profiles_sleep"),
        CheckConstraint("available_workout_days IS NULL OR (available_workout_days >= 1 AND available_workout_days <= 7)", name="ck_health_profiles_workout_days"),
        CheckConstraint("available_workout_minutes IS NULL OR (available_workout_minutes >= 5 AND available_workout_minutes <= 300)", name="ck_health_profiles_workout_mins"),
        UniqueConstraint("user_id", name="uq_health_profiles_user_id"),
    )

    # ── Relationship ───────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="health_profile",
    )

    # ── Helpers ────────────────────────────────────────────────
    def compute_bmi(self) -> Optional[float]:
        """
        Compute and cache BMI from current height and weight.
        Call this whenever height_cm or weight_kg is updated.
        Returns None if either value is missing.
        """
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = self.height_cm / 100
            self.bmi = round(self.weight_kg / (height_m ** 2), 2)
            return self.bmi
        return None

    @property
    def bmi_category(self) -> Optional[str]:
        """Returns WHO BMI classification string."""
        if self.bmi is None:
            return None
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25.0:
            return "Normal weight"
        elif self.bmi < 30.0:
            return "Overweight"
        else:
            return "Obese"

    def __repr__(self) -> str:
        return (
            f"<HealthProfile user_id={self.user_id} "
            f"goal={self.fitness_goal} bmi={self.bmi}>"
        )
