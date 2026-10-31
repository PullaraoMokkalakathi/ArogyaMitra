import { API_V1_URL, getAuthHeaders, parseErrorMessage } from "./client";

const API_BASE = `${API_V1_URL}/workout`;

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

export async function getWorkoutPlan(): Promise<WorkoutPlanResponse> {
  const response = await fetch(`${API_BASE}/plan`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to fetch workout plan" }));
    throw new Error(parseErrorMessage(error, "Failed to fetch workout plan"));
  }

  return response.json();
}
