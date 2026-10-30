const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const API_BASE = `${BASE_URL}/api/v1`;

export interface MacroData {
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface MealData {
  name: string;
  items: string[];
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface GroceryItem {
  name: string;
  category: string;
  bigbasket_url: string;
}

export interface NutritionPlanResponse {
  goal: string;
  daily_calories: number;
  hydration_liters: number;
  macros: MacroData;
  breakfast: MealData;
  lunch: MealData;
  dinner: MealData;
  snacks: MealData[];
  grocery_list: GroceryItem[];
}

export const getNutritionPlan = async (): Promise<NutritionPlanResponse> => {
  const token = localStorage.getItem("access_token");
  if (!token) throw new Error("Not authenticated");

  const response = await fetch(`${API_BASE}/nutrition/plan`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || "Failed to fetch nutrition plan");
  }

  return response.json();
};
