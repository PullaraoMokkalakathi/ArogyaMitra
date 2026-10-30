import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getNutritionPlan, NutritionPlanResponse, MealData } from "../api/nutrition";

export default function NutritionPage() {
  const navigate = useNavigate();
  const [plan, setPlan] = useState<NutritionPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPlan = async () => {
      try {
        const data = await getNutritionPlan();
        setPlan(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load nutrition plan");
      } finally {
        setLoading(false);
      }
    };
    loadPlan();
  }, []);

  const MealCard = ({ title, meal, icon }: { title: string; meal: MealData; icon: string }) => (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-xl backdrop-blur-lg">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <h3 className="font-semibold text-white">{title}</h3>
      </div>
      <div className="mt-3">
        <p className="font-medium text-cyan-400">{meal.name}</p>
        <p className="mt-1 text-sm text-cyan-200/70">{meal.calories} kcal • P: {meal.protein_g}g • C: {meal.carbs_g}g • F: {meal.fat_g}g</p>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {meal.items.map((item, idx) => (
          <span key={idx} className="rounded-full border border-white/5 bg-white/10 px-2 py-1 text-xs text-white">
            {item}
          </span>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 via-gray-950 to-black px-4 py-8">
      <div className="w-full max-w-5xl space-y-6 rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-white">Nutrition Plan</h1>
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
            <p className="mt-4 text-center text-cyan-200/50">Nutrition plan will be available once you complete onboarding</p>
          </div>
        )}

        {loading ? (
          <p className="text-cyan-200/50">Generating your personalized nutrition plan...</p>
        ) : plan ? (
          <div className="space-y-8">
            {/* Summary Section */}
            <div className="grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center shadow-lg">
                <p className="text-xs text-cyan-200/70">Daily Target</p>
                <p className="text-2xl font-bold text-cyan-400">{plan.daily_calories}</p>
                <p className="text-xs text-cyan-200/50">kcal</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center shadow-lg">
                <p className="text-xs text-cyan-200/70">Protein</p>
                <p className="text-2xl font-bold text-white">{plan.macros.protein_g}g</p>
                <p className="text-xs text-cyan-200/50">target</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center shadow-lg">
                <p className="text-xs text-cyan-200/70">Carbs / Fat</p>
                <p className="text-2xl font-bold text-white">{plan.macros.carbs_g}g / {plan.macros.fat_g}g</p>
                <p className="text-xs text-cyan-200/50">macros</p>
              </div>
              <div className="rounded-2xl border border-blue-500/20 bg-blue-900/20 p-4 text-center shadow-lg">
                <p className="text-xs text-blue-300/70">Hydration</p>
                <p className="text-2xl font-bold text-blue-400">{plan.hydration_liters}</p>
                <p className="text-xs text-blue-300/50">Liters / day</p>
              </div>
            </div>

            {/* Meals Section */}
            <div>
              <h2 className="mb-4 text-xl font-semibold text-white">Daily Menu</h2>
              <div className="grid gap-4 md:grid-cols-2">
                <MealCard title="Breakfast" meal={plan.breakfast} icon="🍳" />
                <MealCard title="Lunch" meal={plan.lunch} icon="🥗" />
                <MealCard title="Dinner" meal={plan.dinner} icon="🥘" />
                {plan.snacks.map((snack, idx) => (
                  <MealCard key={idx} title={`Snack ${idx + 1}`} meal={snack} icon="🍎" />
                ))}
              </div>
            </div>

            {/* Grocery Section */}
            <div>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Smart Grocery List</h2>
                <span className="rounded-full bg-green-500/20 px-3 py-1 text-xs text-green-400">Powered by BigBasket</span>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                {plan.grocery_list.map((item, idx) => (
                  <a
                    key={idx}
                    href={item.bigbasket_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 p-3 hover:bg-white/10 hover:shadow-lg transition-all"
                  >
                    <span className="text-sm font-medium text-white">{item.name}</span>
                    <span className="flex items-center gap-1 text-xs text-green-400">
                      Shop →
                    </span>
                  </a>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/2 p-12">
            <p className="text-center text-cyan-200/50">Complete onboarding to generate your nutrition plan</p>
          </div>
        )}
      </div>
    </div>
  );
}