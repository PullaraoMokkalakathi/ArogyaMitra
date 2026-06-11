const API_BASE = "http://127.0.0.1:8000/api/v1/workout";

export interface WorkoutExercise {
  name: string;
  sets: number;
  reps: number;
  duration_minutes: number | null;
  rest_seconds: number;
  intensity: "low" | "medium" | "high";
}

export interface WorkoutDay {
  day: string;
  focus: string;
  exercises: WorkoutExercise[];
  total_duration_minutes: number;
  is_rest_day: boolean;
}

export interface WorkoutPlanResponse {
  goal: string;
  level: string;
  bmi: number;
  daily_duration_minutes: number;
  weekly_plan: WorkoutDay[];
}

function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function getWorkoutPlan(): Promise<WorkoutPlanResponse> {
  const response = await fetch(`${API_BASE}/plan`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to fetch workout plan" }));
    throw new Error(error.detail || "Failed to fetch workout plan");
  }

  return response.json();
}