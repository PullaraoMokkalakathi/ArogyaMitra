import api from "./auth";

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

  const response = await fetch("http://127.0.0.1:8000/api/v1/nutrition/plan", {
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
