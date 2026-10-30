import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.models.progress import ProgressLog
from app.schemas.progress import ProgressCreateRequest, ProgressResponse, ProgressStatsResponse, DailyStats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post("/log", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
def log_progress(payload: ProgressCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    last_log = db.query(ProgressLog).filter(ProgressLog.user_id == current_user.id).order_by(ProgressLog.workout_date.desc()).first()
    
    new_streak = 1
    today = datetime.now(timezone.utc).date()
    
    if last_log:
        last_date = last_log.workout_date.date()
        if (today - last_date).days == 1:
            new_streak = last_log.streak_day + 1
        elif (today - last_date).days == 0:
            new_streak = last_log.streak_day

    log = ProgressLog(
        user_id=current_user.id,
        streak_day=new_streak,
        **payload.model_dump()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return ProgressResponse.model_validate(log)

@router.get("/stats", response_model=ProgressStatsResponse)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    logs = db.query(ProgressLog).filter(ProgressLog.user_id == current_user.id).order_by(ProgressLog.workout_date.desc()).all()
    
    total_workouts = len(logs)
    total_minutes = sum(l.duration_minutes for l in logs)
    total_calories = sum(l.calories_burned for l in logs)
    best_score = max((l.posture_score for l in logs), default=0.0)
    current_streak = logs[0].streak_day if logs else 0
    best_streak = max((l.streak_day for l in logs), default=0)
    
    from collections import defaultdict
    weekly = defaultdict(lambda: {"workouts": 0, "cals": 0.0, "scores": []})
    
    for l in logs[:30]:
        d_str = l.workout_date.strftime("%a")
        weekly[d_str]["workouts"] += 1
        weekly[d_str]["cals"] += l.calories_burned
        weekly[d_str]["scores"].append(l.posture_score)
        
    weekly_history = []
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days_order:
        data = weekly.get(day, {"workouts": 0, "cals": 0.0, "scores": []})
        avg_s = sum(data["scores"])/len(data["scores"]) if data["scores"] else 0.0
        weekly_history.append(DailyStats(date=day, workouts=data["workouts"], calories=data["cals"], avg_score=avg_s))

    return ProgressStatsResponse(
        total_workouts=total_workouts,
        total_minutes=total_minutes,
        total_calories=total_calories,
        current_streak=current_streak,
        best_streak=best_streak,
        best_posture_score=best_score,
        weekly_history=weekly_history,
        recent_logs=[ProgressResponse.model_validate(l) for l in logs[:5]]
    )
