import { API_V1_URL, getAuthHeaders, parseErrorMessage } from "./client";

const API_BASE = `${API_V1_URL}/nutrition`;

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
  const response = await fetch(`${API_BASE}/plan`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(parseErrorMessage(errorData, "Failed to fetch nutrition plan"));
  }

  return response.json();
};
