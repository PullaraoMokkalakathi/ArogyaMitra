from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    workout_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(100), nullable=False)
    workout_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    reps_completed: Mapped[int] = mapped_column(Integer, default=0)
    calories_burned: Mapped[float] = mapped_column(Float, default=0.0)
    posture_score: Mapped[float] = mapped_column(Float, default=0.0)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    streak_day: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    user: Mapped["User"] = relationship("User")
