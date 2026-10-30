import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { getWorkoutPlan, WorkoutPlanResponse } from "../api/workout";
import CameraCoach from "../components/CameraCoach";
import { logProgress } from "../api/progress";
import { getWorkoutVideo } from "../utils/workoutVideos";

export default function WorkoutPage() {
  const navigate = useNavigate();
  const [plan, setPlan] = useState<WorkoutPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Exercise Session State
  const [activeExercise, setActiveExercise] = useState<string | null>(null);
  const [reps, setReps] = useState(0);
  const [score, setScore] = useState(100);
  const [feedback, setFeedback] = useState("Initializing Local AI...");
  const [sessionTime, setSessionTime] = useState(0);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    const loadPlan = async () => {
      try {
        const data = await getWorkoutPlan();
        setPlan(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load workout plan");
      } finally {
        setLoading(false);
      }
    };
    loadPlan();
  }, []);

  // Timer logic for active session
  useEffect(() => {
    if (activeExercise) {
      setSessionTime(0);
      setReps(0);
      setScore(100);
      setFeedback("Ready to start");
      timerRef.current = window.setInterval(() => {
        setSessionTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [activeExercise]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  const handleEndSession = async () => {
    if (!activeExercise) return;
    try {
      await logProgress({
        exercise_name: activeExercise,
        duration_minutes: Math.ceil(sessionTime / 60) || 1,
        reps_completed: reps,
        calories_burned: Math.round(sessionTime * 0.15) || 1,
        posture_score: score,
        completion_percentage: 100,
      });
      setActiveExercise(null);
    } catch (err) {
      console.error(err);
      setActiveExercise(null);
    }
  };

  // ── ACTIVE SESSION UI ────────────────────────────────────────────────────────
  if (activeExercise) {
    return (
      <div className="flex min-h-screen flex-col bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4 py-8">
        <div className="mx-auto w-full max-w-7xl space-y-6">
          <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
            <div>
              <h1 className="text-3xl font-bold text-cyan-400">{activeExercise}</h1>
              <p className="text-cyan-200/70 font-mono text-lg">{formatTime(sessionTime)}</p>
            </div>
            <button
              onClick={handleEndSession}
              className="rounded-lg bg-red-600/80 hover:bg-red-500 px-6 py-2 text-sm font-semibold text-white shadow-lg transition-all"
            >
              End Session
            </button>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* LEFT PANEL: Live AI Coach Session */}
            <div className="space-y-6 flex flex-col">
              <div className="rounded-2xl border border-cyan-500/30 bg-white/5 p-4 shadow-[0_0_20px_rgba(34,211,238,0.1)] backdrop-blur-lg relative overflow-hidden flex-1 flex flex-col">
                <h3 className="mb-4 text-lg font-semibold text-white">Live AI Coach</h3>
                <div className="flex-1 w-full rounded-xl overflow-hidden border border-white/10 relative min-h-[300px]">
                  <CameraCoach 
                    exercise={activeExercise}
                    onUpdateReps={setReps}
                    onUpdateScore={setScore}
                    onUpdateFeedback={setFeedback}
                  />
                  <div className="absolute top-4 left-4 bg-black/60 px-3 py-1 rounded-md border border-white/10 backdrop-blur-md flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                    <span className="text-xs text-white font-medium uppercase tracking-wider">Live</span>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="rounded-xl border border-white/10 bg-black/30 p-4 text-center">
                    <p className="text-xs text-cyan-200/70">Reps Count</p>
                    <p className="mt-1 text-4xl font-bold text-white">{reps}</p>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-black/30 p-4 text-center">
                    <p className="text-xs text-cyan-200/70">Accuracy</p>
                    <p className={`mt-1 text-4xl font-bold ${score > 80 ? 'text-green-400' : 'text-orange-400'}`}>
                      {score}%
                    </p>
                  </div>
                </div>

                <div className="mt-4 rounded-xl border border-white/10 bg-black/30 p-4">
                  <p className="text-xs text-cyan-200/70">Real-time Feedback</p>
                  <p className="mt-1 text-xl font-semibold text-cyan-400">{feedback}</p>
                </div>
              </div>
            </div>

            {/* RIGHT PANEL: YouTube Reference */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-2xl backdrop-blur-lg flex flex-col">
              <h3 className="mb-4 text-lg font-semibold text-white">Tutorial Reference</h3>
              <div className="w-full flex-1 min-h-[400px] rounded-xl overflow-hidden border border-white/10 bg-black">
                <iframe
                  key={activeExercise}
                  src={getWorkoutVideo(activeExercise!)}
                  width="100%"
                  height="100%"
                  title="Workout Tutorial"
                  allowFullScreen
                  frameBorder="0"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── WORKOUT LIST UI ────────────────────────────────────────────────────────
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4 py-8">
      <div className="w-full max-w-4xl space-y-6 rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-white">Workout Plan</h1>
          <button
            onClick={() => navigate("/dashboard")}
            className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-cyan-200 shadow-lg shadow-cyan-600/25 backdrop-blur-sm transition-all hover:bg-white/10"
          >
            ← Back
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-600/20 p-4">
            <p className="text-sm text-red-300">{error}</p>
            <p className="mt-4 text-center text-cyan-200/50">Workout plan will be available once you complete onboarding</p>
          </div>
        )}

        {loading ? (
          <p className="text-cyan-200/50">Loading workout plan...</p>
        ) : plan ? (
          <div className="space-y-6">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <h2 className="text-lg font-semibold text-white capitalize">{plan.goal.replace("_", " ")} Program</h2>
              <p className="mt-1 text-sm text-cyan-200/70">Level: {plan.level} | Daily Duration: {plan.daily_duration_minutes} min | BMI: {plan.bmi}</p>
            </div>

            <div className="space-y-4">
              {plan.weekly_plan.map((day) => (
                <div
                  key={day.day}
                  className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-xl backdrop-blur-lg"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-white">{day.day}</h3>
                    <div className="text-xs">
                      {day.is_rest_day ? (
                        <span className="text-green-400">Rest Day</span>
                      ) : (
                        <span className="text-cyan-200/70">{day.focus} • {day.total_duration_minutes} min</span>
                      )}
                    </div>
                  </div>

                  {!day.is_rest_day && day.exercises.length > 0 && (
                    <div className="mt-3 grid gap-3">
                      {day.exercises.map((ex, idx) => (
                        <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between rounded-lg border border-white/5 bg-white/5 p-4 hover:bg-white/10 transition-colors">
                          <div>
                            <p className="font-medium text-cyan-400 text-lg">{ex.name}</p>
                            <p className="text-sm text-cyan-200/70 mt-1">
                              {ex.sets} sets × {ex.reps} reps | Rest: {ex.rest_seconds}s | Intensity: {ex.intensity}
                            </p>
                          </div>
                          <button
                            onClick={() => setActiveExercise(ex.name)}
                            className="mt-3 sm:mt-0 rounded-lg bg-cyan-600/20 px-4 py-2 text-sm font-semibold text-cyan-300 hover:bg-cyan-600/40 border border-cyan-500/30 transition-all shadow-[0_0_15px_rgba(34,211,238,0.15)]"
                          >
                            Start Exercise
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {!day.is_rest_day && day.exercises.length === 0 && (
                    <p className="mt-3 text-sm text-cyan-200/50">No exercises scheduled</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/2 p-12">
            <p className="text-center text-cyan-200/50">Complete onboarding to generate your workout plan</p>
          </div>
        )}
      </div>
    </div>
  );
}