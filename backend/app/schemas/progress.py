from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class ProgressCreateRequest(BaseModel):
    exercise_name: str
    workout_type: Optional[str] = None
    duration_minutes: int
    reps_completed: int
    calories_burned: float
    posture_score: float
    completion_percentage: float
    notes: Optional[str] = None

class ProgressResponse(ProgressCreateRequest):
    id: int
    user_id: int
    workout_date: datetime
    streak_day: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DailyStats(BaseModel):
    date: str
    workouts: int
    calories: float
    avg_score: float

class ProgressStatsResponse(BaseModel):
    total_workouts: int
    total_minutes: int
    total_calories: float
    current_streak: int
    best_streak: int
    best_posture_score: float
    weekly_history: List[DailyStats]
    recent_logs: List[ProgressResponse]
