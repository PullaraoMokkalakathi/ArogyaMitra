import { API_V1_URL, getAuthHeaders, parseErrorMessage } from "./client";

const API_BASE = `${API_V1_URL}/progress`;

export interface ProgressCreateRequest {
  exercise_name: string;
  workout_type?: string;
  duration_minutes: number;
  reps_completed: number;
  calories_burned: number;
  posture_score: number;
  completion_percentage: number;
  notes?: string;
}

export interface ProgressResponse extends ProgressCreateRequest {
  id: number;
  user_id: number;
  workout_date: string;
  streak_day: number;
}

export interface DailyStats {
  date: string;
  workouts: number;
  calories: number;
  avg_score: number;
}

export interface ProgressStatsResponse {
  total_workouts: number;
  total_minutes: number;
  total_calories: number;
  current_streak: number;
  best_streak: number;
  best_posture_score: number;
  weekly_history: DailyStats[];
  recent_logs: ProgressResponse[];
}

export const logProgress = async (data: ProgressCreateRequest): Promise<ProgressResponse> => {
  const res = await fetch(`${API_BASE}/log`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Failed to log progress" }));
    throw new Error(parseErrorMessage(errorData, "Failed to log progress"));
  }
  return res.json();
};

export const getProgressStats = async (): Promise<ProgressStatsResponse> => {
  const res = await fetch(`${API_BASE}/stats`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Failed to load progress stats" }));
    throw new Error(parseErrorMessage(errorData, "Failed to load progress stats"));
  }
  return res.json();
};
