import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CameraCoach, { ExerciseType } from "../components/CameraCoach";
import { logProgress } from "../api/progress";

export default function CoachPage() {
  const navigate = useNavigate();
  const [exercise, setExercise] = useState<ExerciseType>("Squats");
  const [reps, setReps] = useState(0);
  const [score, setScore] = useState(100);
  const [feedback, setFeedback] = useState("Initializing Local AI...");
  const [sessionTime, setSessionTime] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSessionTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  const handleEndSession = async () => {
    try {
      await logProgress({
        exercise_name: exercise,
        duration_minutes: Math.ceil(sessionTime / 60),
        reps_completed: reps,
        calories_burned: Math.round(sessionTime * 0.15) || 1, // rough estimate
        posture_score: score,
        completion_percentage: 100,
      });
      navigate("/progress");
    } catch (err) {
      console.error(err);
      navigate("/progress"); // Navigate anyway on error for fallback
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4 py-8">
      <div className="mx-auto w-full max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
          <div>
            <h1 className="text-3xl font-bold text-white">AI Posture Coach</h1>
            <p className="text-cyan-200/70">Real-time local tracking via MediaPipe Pose Engine</p>
          </div>
          <button
            onClick={() => navigate("/dashboard")}
            className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-cyan-200 transition-all hover:bg-white/10"
          >
            ← Back
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Camera View */}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-2xl backdrop-blur-lg lg:col-span-2">
             <CameraCoach 
               exercise={exercise}
               onUpdateReps={setReps}
               onUpdateScore={setScore}
               onUpdateFeedback={setFeedback}
             />
          </div>

          {/* Sidebar / HUD */}
          <div className="space-y-6">
            {/* Exercise Selector */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
              <h3 className="mb-4 text-lg font-semibold text-white">Select Exercise</h3>
              <select
                value={exercise}
                onChange={(e) => setExercise(e.target.value as ExerciseType)}
                className="w-full rounded-lg border border-white/10 bg-gray-900 px-4 py-3 text-lg font-medium text-cyan-400 outline-none focus:border-cyan-400"
              >
                <option value="Squats">Squats</option>
                <option value="Pushups">Pushups</option>
                <option value="Lunges">Lunges</option>
                <option value="Planks">Planks</option>
              </select>
            </div>

            {/* Live Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center shadow-xl backdrop-blur-lg">
                <p className="text-xs text-cyan-200/70">Reps</p>
                <p className="mt-1 text-5xl font-bold text-white">{reps}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center shadow-xl backdrop-blur-lg relative overflow-hidden">
                <div className={`absolute inset-0 opacity-10 ${score > 80 ? 'bg-green-500' : 'bg-orange-500'}`} />
                <p className="text-xs text-cyan-200/70 relative z-10">Accuracy</p>
                <p className={`mt-1 text-5xl font-bold relative z-10 ${score > 80 ? 'text-green-400' : 'text-orange-400'}`}>
                  {score}%
                </p>
              </div>
            </div>

            {/* Feedback Panel */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
              <h3 className="text-sm font-medium text-cyan-200/70">Live Feedback</h3>
              <p className="mt-2 text-2xl font-semibold text-cyan-400 min-h-[4rem] flex items-center">
                {feedback}
              </p>
            </div>

            {/* Session Status */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-cyan-200/70">Session Time</span>
                <span className="font-mono text-xl text-white">{formatTime(sessionTime)}</span>
              </div>
              <div className="mt-4 flex items-center justify-between mb-6">
                <span className="text-sm font-medium text-cyan-200/70">Engine Status</span>
                <span className="flex items-center gap-2 text-sm font-medium text-green-400">
                  <span className="h-3 w-3 rounded-full bg-green-400 animate-pulse shadow-[0_0_10px_rgba(74,222,128,0.5)]" />
                  Local AI Active
                </span>
              </div>
              <button 
                onClick={handleEndSession}
                className="w-full rounded-lg bg-red-600/80 hover:bg-red-500 py-3 font-semibold text-white transition-all shadow-lg shadow-red-600/30"
              >
                End Session & Save Progress
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}