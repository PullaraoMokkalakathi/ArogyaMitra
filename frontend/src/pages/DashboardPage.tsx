import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchHealthProfile, HealthProfileResponse } from "../api/health";
import { Link } from "react-router-dom";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<HealthProfileResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const calculateBMI = (weightKg: number, heightCm: number): number => {
    const heightM = heightCm / 100;
    return Math.round(weightKg / (heightM * heightM));
  };

  const getBMIStatus = (bmi: number): string => {
    if (bmi < 18.5) return "Underweight";
    if (bmi < 25) return "Normal";
    if (bmi < 30) return "Overweight";
    return "Obese";
  };

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await fetchHealthProfile();
        setProfile(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load profile");
      }
    };
    loadProfile();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black">
      <nav className="border-b border-white/10 bg-white/5 px-4 py-4 backdrop-blur-lg">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">Dashboard</h1>
            <p className="text-sm text-cyan-200/70">Level up your fitness journey</p>
          </div>
          <button
            onClick={handleLogout}
            className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-cyan-200 shadow-lg shadow-cyan-600/25 backdrop-blur-sm transition-all hover:bg-white/10"
          >
            Logout
          </button>
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {error && (
          <div className="mb-6 rounded-lg border border-red-500/30 bg-red-600/20 p-4">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        <div className="mb-8 rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg">
          <h2 className="text-3xl font-bold text-white">
            Welcome{profile?.age ? `, Champion` : ", Warrior"}!
          </h2>
          <p className="mt-2 text-cyan-200/70">
            Your personalized fitness journey starts now. Track progress, crush goals.
          </p>
        </div>

        <div className="mb-8 grid gap-6 md:grid-cols-5">
          {[
            { label: "BMI", value: profile ? calculateBMI(profile.weight_kg, profile.height_cm).toString() : "—", sub: profile ? getBMIStatus(calculateBMI(profile.weight_kg, profile.height_cm)) : undefined },
            { label: "Weight", value: profile ? `${profile.weight_kg} kg` : "—", sub: undefined },
            { label: "Height", value: profile ? `${profile.height_cm} cm` : "—", sub: undefined },
            { label: "Goal", value: profile?.fitness_goal.replace("_", " ") || "—", sub: undefined },
            { label: "Activity", value: profile?.activity_level.replace("_", " ") || "—", sub: undefined },
          ].map((item) => (
            <div
              key={item.label}
              className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg transition-all hover:bg-white/10"
            >
              <p className="text-sm text-cyan-200/70">{item.label}</p>
              <p className="mt-1 text-2xl font-semibold text-cyan-400">{item.value}</p>
              {item.sub && <p className="text-xs text-cyan-200/50">{item.sub}</p>}
            </div>
          ))}
        </div>

        <div className="mb-8 grid gap-6 md:grid-cols-4">
          {[
            { title: "Workout Plan", desc: "Personalized routines", icon: "💪", to: "/workout" },
            { title: "Nutrition Plan", desc: "Meal guidance", icon: "🥗", to: "/nutrition" },
            { title: "Progress", desc: "Monitor gains", icon: "📊", to: "/progress" },
            { title: "AI Coach", desc: "Ask anything", icon: "🤖", to: "/chat" },
            { title: "Camera Coach", desc: "Live form check", icon: "📷", to: "/coach" },
          ].map((card) => (
            <Link
              key={card.title}
              to={card.to}
              className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg transition-all hover:bg-white/10 hover:shadow-cyan-600/40"
            >
              <div className="text-3xl">{card.icon}</div>
              <h3 className="mt-3 font-semibold text-white">{card.title}</h3>
              <p className="mt-1 text-sm text-cyan-200/70">{card.desc}</p>
            </Link>
          ))}
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
          <h3 className="text-lg font-semibold text-white">Profile</h3>
          <div className="mt-4 flex items-center justify-between">
            <div>
              <p className="text-cyan-200/70">Email</p>
              <p className="font-medium text-cyan-400">user@example.com</p>
            </div>
            <div>
              <p className="text-cyan-200/70">Role</p>
              <p className="font-medium text-cyan-400">Member</p>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-cyan-200 shadow-lg shadow-cyan-600/25 backdrop-blur-sm transition-all hover:bg-white/10"
            >
              Logout
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}