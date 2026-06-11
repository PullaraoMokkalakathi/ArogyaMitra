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
  const token = localStorage.getItem("access_token");
  const res = await fetch("http://127.0.0.1:8000/api/v1/progress/log", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error("Failed to log progress");
  return res.json();
};

export const getProgressStats = async (): Promise<ProgressStatsResponse> => {
  const token = localStorage.getItem("access_token");
  const res = await fetch("http://127.0.0.1:8000/api/v1/progress/stats", {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to load progress stats");
  return res.json();
};
