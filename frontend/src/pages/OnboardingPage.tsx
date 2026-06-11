import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createHealthProfile, HealthProfile } from "../api/health";

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [fitnessGoal, setFitnessGoal] = useState("");
  const [activityLevel, setActivityLevel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const profile: HealthProfile = {
      age: parseInt(age, 10),
      gender,
      height_cm: parseFloat(heightCm),
      weight_kg: parseFloat(weightKg),
      fitness_goal: fitnessGoal,
      activity_level: activityLevel,
    };

    try {
      await createHealthProfile(profile);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-white">Health Assessment</h1>
          <p className="mt-2 text-sm text-cyan-200/70">Complete your profile setup</p>
        </div>
        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-600/20 p-3">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="age" className="block text-sm font-medium text-cyan-200">
              Age
            </label>
            <input
              id="age"
              type="number"
              required
              value={age}
              onChange={(e) => setAge(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
              placeholder="25"
            />
          </div>
          <div>
            <label htmlFor="gender" className="block text-sm font-medium text-cyan-200">
              Gender
            </label>
            <select
              id="gender"
              required
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
            >
              <option value="" className="bg-gray-900">
                Select gender
              </option>
              <option value="male" className="bg-gray-900">
                Male
              </option>
              <option value="female" className="bg-gray-900">
                Female
              </option>
              <option value="other" className="bg-gray-900">
                Other
              </option>
            </select>
          </div>
          <div>
            <label htmlFor="height_cm" className="block text-sm font-medium text-cyan-200">
              Height (cm)
            </label>
            <input
              id="height_cm"
              type="number"
              required
              value={heightCm}
              onChange={(e) => setHeightCm(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
              placeholder="175"
            />
          </div>
          <div>
            <label htmlFor="weight_kg" className="block text-sm font-medium text-cyan-200">
              Weight (kg)
            </label>
            <input
              id="weight_kg"
              type="number"
              step="0.1"
              required
              value={weightKg}
              onChange={(e) => setWeightKg(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
              placeholder="70.5"
            />
          </div>
          <div>
            <label htmlFor="fitness_goal" className="block text-sm font-medium text-cyan-200">
              Fitness Goal
            </label>
            <select
              id="fitness_goal"
              required
              value={fitnessGoal}
              onChange={(e) => setFitnessGoal(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
            >
              <option value="" className="bg-gray-900">
                Select goal
              </option>
              <option value="weight_loss" className="bg-gray-900">
                Lose Weight
              </option>
              <option value="muscle_gain" className="bg-gray-900">
                Muscle Gain
              </option>
              <option value="maintenance" className="bg-gray-900">
                Maintain
              </option>
            </select>
          </div>
          <div>
            <label htmlFor="activity_level" className="block text-sm font-medium text-cyan-200">
              Activity Level
            </label>
            <select
              id="activity_level"
              required
              value={activityLevel}
              onChange={(e) => setActivityLevel(e.target.value)}
              disabled={loading}
              className="mt-1 block w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white shadow-sm backdrop-blur-sm transition-all focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
            >
              <option value="" className="bg-gray-900">
                Select level
              </option>
              <option value="sedentary" className="bg-gray-900">
                Sedentary
              </option>
              <option value="light" className="bg-gray-900">
                Light
              </option>
              <option value="moderate" className="bg-gray-900">
                Moderate
              </option>
              <option value="active" className="bg-gray-900">
                Active
              </option>
              <option value="very_active" className="bg-gray-900">
                Very Active
              </option>
            </select>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-cyan-600/80 px-4 py-2 text-sm font-medium text-white shadow-lg shadow-cyan-600/25 transition-all hover:bg-cyan-500 hover:shadow-cyan-500/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-gray-950 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Saving..." : "Save Profile"}
          </button>
        </form>
      </div>
    </div>
  );
}