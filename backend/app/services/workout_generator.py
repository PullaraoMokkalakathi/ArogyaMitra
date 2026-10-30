# ──────────────────────────────────────────────────────────────
# app/services/workout_generator.py
# PROFESSIONAL AI workout recommendation engine
# ──────────────────────────────────────────────────────────────

import random
from dataclasses import dataclass
from typing import Literal, Optional
from enum import Enum

class FitnessGoal(str, Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    maintenance = "maintenance"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"

@dataclass
class WorkoutExercise:
    name: str
    sets: int
    reps: int
    duration_minutes: Optional[int] = None
    rest_seconds: int = 60
    intensity: Literal["low", "medium", "high"] = "medium"

@dataclass
class WorkoutDay:
    day: str
    focus: str
    exercises: list[WorkoutExercise]
    total_duration_minutes: int
    is_rest_day: bool = False

@dataclass
class WorkoutPlan:
    goal: str
    level: str
    daily_duration_minutes: int
    weekly_plan: list[WorkoutDay]
    bmi: Optional[float] = None

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ── Exercise Database by Category ──────────────────────────────────────
CHEST = ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Pushups", "Cable Crossovers"]
BACK = ["Pullups", "Barbell Row", "Lat Pulldown", "Deadlift", "Face Pulls", "Seated Cable Row"]
LEGS = ["Squats", "Leg Press", "Lunges", "Calf Raises", "Romanian Deadlift", "Leg Extensions"]
SHOULDERS = ["Shoulder Press", "Lateral Raises", "Front Raises", "Reverse Pec Deck"]
ARMS = ["Bicep Curl", "Tricep Pushdown", "Hammer Curls", "Overhead Tricep Extension", "Dips"]
CORE = ["Plank", "Crunches", "Leg Raises", "Russian Twists", "Ab Wheel Rollout"]
CARDIO = ["Running", "Cycling", "Jump Rope", "Rowing Machine", "Stairmaster"]
HIIT = ["Burpees", "Mountain Climbers", "Jump Squats", "Kettlebell Swings", "Box Jumps"]
MOBILITY = ["Yoga Flow", "Dynamic Stretching", "Foam Rolling", "Cat-Cow", "Hip Openers"]

SAFE_BEGINNER = ["Bodyweight Squats", "Pushups (Knees)", "Plank", "Walking Lunges", "Dumbbell Press"]
LOW_IMPACT = ["Swimming", "Stationary Bike", "Elliptical", "Water Aerobics", "Seated Row"]

def _calculate_bmi(height_cm: float, weight_kg: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def _get_age_group(age: int) -> str:
    if 13 <= age <= 18: return "teen"
    if 19 <= age <= 35: return "young"
    if 36 <= age <= 50: return "middle"
    return "senior"

def _get_training_volume(level: ActivityLevel) -> tuple[int, int]:
    # returns (days_per_week, duration_minutes)
    mapping = {
        ActivityLevel.sedentary: (3, 30),
        ActivityLevel.light: (4, 45),
        ActivityLevel.moderate: (5, 60),
        ActivityLevel.active: (6, 75),
        ActivityLevel.very_active: (6, 90),
    }
    return mapping.get(level, (4, 45))

def _get_split(goal: FitnessGoal, days: int) -> list[tuple[str, list[str]]]:
    """Returns a list of (Focus, [Category Lists]) representing the weekly split."""
    if goal == FitnessGoal.muscle_gain:
        if days <= 3:
            return [
                ("Full Body A", [CHEST, BACK, LEGS, CORE]),
                ("Rest", []),
                ("Full Body B", [SHOULDERS, ARMS, LEGS, CORE]),
                ("Rest", []),
                ("Full Body C", [CHEST, BACK, LEGS, ARMS]),
                ("Rest", []),
                ("Rest", [])
            ]
        elif days <= 4:
            return [
                ("Upper Body", [CHEST, BACK, SHOULDERS, ARMS]),
                ("Lower Body", [LEGS, CORE]),
                ("Rest", []),
                ("Upper Body", [CHEST, BACK, SHOULDERS, ARMS]),
                ("Lower Body", [LEGS, CORE]),
                ("Rest", []),
                ("Rest", [])
            ]
        else: # 5 or 6 days (Bro Split / PPL)
            return [
                ("Chest & Triceps", [CHEST, ARMS]),
                ("Back & Biceps", [BACK, ARMS]),
                ("Legs", [LEGS]),
                ("Shoulders & Core", [SHOULDERS, CORE]),
                ("Upper Body Strength", [CHEST, BACK, SHOULDERS]),
                ("Cardio & Mobility", [CARDIO, MOBILITY]) if days == 6 else ("Rest", []),
                ("Rest", [])
            ]

    elif goal == FitnessGoal.weight_loss:
        if days <= 4:
            return [
                ("Full Body HIIT", [HIIT, CORE]),
                ("Rest", []),
                ("Strength & Fat Burn", [CHEST, LEGS, CARDIO]),
                ("Rest", []),
                ("Cardio & Core", [CARDIO, CORE]),
                ("Mobility", [MOBILITY]),
                ("Rest", [])
            ]
        else:
            return [
                ("Full Body HIIT", [HIIT, CORE]),
                ("Cardio & Core", [CARDIO, CORE]),
                ("Strength & Fat Burn", [BACK, LEGS, HIIT]),
                ("Mobility", [MOBILITY]),
                ("Lower Body", [LEGS, CORE]),
                ("Upper Body", [CHEST, BACK, SHOULDERS]),
                ("Rest", [])
            ]

    else: # maintenance
        return [
            ("Push Day", [CHEST, SHOULDERS, ARMS]),
            ("Pull Day", [BACK, ARMS, CORE]),
            ("Leg Day", [LEGS, CORE]),
            ("Active Recovery", [MOBILITY, CARDIO]),
            ("Full Body", [CHEST, BACK, LEGS]),
            ("Rest", []),
            ("Rest", [])
        ][:7] # simplified for maintenance

def generate_workout_plan(age: int, gender: str, height_cm: float, weight_kg: float, fitness_goal: str, activity_level: str) -> WorkoutPlan:
    goal = FitnessGoal(fitness_goal) if fitness_goal in [g.value for g in FitnessGoal] else FitnessGoal.maintenance
    level = ActivityLevel(activity_level) if activity_level in [a.value for a in ActivityLevel] else ActivityLevel.moderate
    bmi = _calculate_bmi(height_cm, weight_kg)
    age_group = _get_age_group(age)
    
    days_per_week, daily_duration = _get_training_volume(level)
    split_blueprint = _get_split(goal, days_per_week)
    
    # Adjust for age/experience
    if age_group == "senior" or bmi >= 30:
        intensity = "low"
        sets, reps = 3, 12
        pool_modifier = LOW_IMPACT
    elif age_group == "teen":
        intensity = "medium"
        sets, reps = 3, 15
        pool_modifier = SAFE_BEGINNER
    else:
        intensity = "high" if level in [ActivityLevel.active, ActivityLevel.very_active] else "medium"
        if goal == FitnessGoal.muscle_gain:
            sets, reps = 4, 8
        elif goal == FitnessGoal.weight_loss:
            sets, reps = 3, 15
        else:
            sets, reps = 3, 10
            
    weekly_plan = []
    
    # Fill actual exercises from blueprint
    for i, day_name in enumerate(DAYS_OF_WEEK):
        if i >= len(split_blueprint):
            focus, categories = "Rest", []
        else:
            focus, categories = split_blueprint[i]
            
        if focus == "Rest" or not categories:
            weekly_plan.append(WorkoutDay(day=day_name, focus="Recovery", exercises=[], total_duration_minutes=0, is_rest_day=True))
            continue
            
        daily_exercises = []
        for cat in categories:
            # Pick 1-2 exercises per category safely
            num_ex = 2 if goal == FitnessGoal.muscle_gain and len(categories) <= 2 else 1
            available = list(set(cat).intersection(pool_modifier)) if age_group in ["teen", "senior"] else cat
            if not available: available = cat # fallback
            
            chosen = random.sample(available, min(num_ex, len(available)))
            for ex_name in chosen:
                rest_sec = 45 if goal == FitnessGoal.weight_loss else 90 if goal == FitnessGoal.muscle_gain else 60
                daily_exercises.append(WorkoutExercise(
                    name=ex_name,
                    sets=sets,
                    reps=reps,
                    duration_minutes=None,
                    rest_seconds=rest_sec,
                    intensity=intensity
                ))
                
        # Shuffle daily exercises slightly for realism
        random.shuffle(daily_exercises)
        total_time = sum((ex.sets * 1.5) + ((ex.sets - 1) * (ex.rest_seconds / 60)) for ex in daily_exercises)
        
        weekly_plan.append(WorkoutDay(
            day=day_name,
            focus=focus,
            exercises=daily_exercises,
            total_duration_minutes=int(total_time) + 10, # Add 10m warmup/cooldown
            is_rest_day=False
        ))
        
    return WorkoutPlan(goal=goal.value, level=level.value, daily_duration_minutes=daily_duration, weekly_plan=weekly_plan, bmi=bmi)

def to_dict(workout_plan: WorkoutPlan) -> dict:
    return {
        "goal": workout_plan.goal,
        "level": workout_plan.level,
        "bmi": workout_plan.bmi,
        "daily_duration_minutes": workout_plan.daily_duration_minutes,
        "weekly_plan": [
            {
                "day": day.day,
                "focus": day.focus,
                "is_rest_day": day.is_rest_day,
                "total_duration_minutes": day.total_duration_minutes,
                "exercises": [
                    {
                        "name": ex.name,
                        "sets": ex.sets,
                        "reps": ex.reps,
                        "duration_minutes": ex.duration_minutes,
                        "rest_seconds": ex.rest_seconds,
                        "intensity": ex.intensity,
                    } for ex in day.exercises
                ],
            } for day in workout_plan.weekly_plan
        ],
    }