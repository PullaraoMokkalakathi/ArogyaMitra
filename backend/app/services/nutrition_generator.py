import random
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Meal:
    name: str
    items: List[str]
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int

@dataclass
class Macros:
    protein_g: int
    carbs_g: int
    fat_g: int

@dataclass
class GroceryItem:
    name: str
    category: str
    bigbasket_url: str

@dataclass
class NutritionPlan:
    goal: str
    daily_calories: int
    hydration_liters: float
    macros: Macros
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    snacks: List[Meal]
    grocery_list: List[GroceryItem]

def _calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    # Mifflin-St Jeor Equation
    if gender == "female":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        # Default to male / other
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5

def _get_activity_multiplier(activity_level: str) -> float:
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    return multipliers.get(activity_level, 1.55)

def _generate_bigbasket_url(item_name: str) -> str:
    query = item_name.replace(" ", "+").lower()
    return f"https://www.bigbasket.com/ps/?q={query}"

def generate_nutrition_plan(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    fitness_goal: str,
    activity_level: str,
    dietary_preference: str,
    allergies: Optional[str] = None,
    food_restrictions: Optional[str] = None
) -> NutritionPlan:
    
    # 1. Calculate TDEE
    bmr = _calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = bmr * _get_activity_multiplier(activity_level)
    
    # 2. Adjust calories based on goal
    if fitness_goal == "weight_loss":
        target_calories = int(tdee - 500)
        protein_ratio = 0.35
        carbs_ratio = 0.35
        fat_ratio = 0.30
    elif fitness_goal == "muscle_gain":
        target_calories = int(tdee + 400)
        protein_ratio = 0.30
        carbs_ratio = 0.50
        fat_ratio = 0.20
    else: # maintenance
        target_calories = int(tdee)
        protein_ratio = 0.30
        carbs_ratio = 0.40
        fat_ratio = 0.30

    # Ensure minimum calories
    target_calories = max(target_calories, 1200)
    
    # 3. Calculate Macros (1g Protein = 4kcal, 1g Carb = 4kcal, 1g Fat = 9kcal)
    protein_g = int((target_calories * protein_ratio) / 4)
    carbs_g = int((target_calories * carbs_ratio) / 4)
    fat_g = int((target_calories * fat_ratio) / 9)
    macros = Macros(protein_g=protein_g, carbs_g=carbs_g, fat_g=fat_g)
    
    # 4. Hydration (Roughly 35ml per kg of body weight)
    hydration_liters = round((weight_kg * 35) / 1000, 1)

    # 5. Base Menus by preference
    is_veg = dietary_preference in ["vegetarian", "vegan"]
    
    b_options = [
        Meal("Oatmeal & Berries", ["Oats", "Mixed Berries", "Almond Milk", "Chia Seeds"], 350, 12, 50, 8),
        Meal("Protein Pancakes", ["Protein Powder", "Oats", "Banana", "Eggs" if not is_veg else "Flax Egg"], 400, 30, 45, 10),
        Meal("Greek Yogurt Parfait", ["Greek Yogurt", "Granola", "Honey", "Strawberries"], 320, 20, 40, 5)
    ]
    
    l_options = [
        Meal("Quinoa Salad Bowl", ["Quinoa", "Chickpeas", "Cucumber", "Olive Oil", "Feta"], 450, 15, 60, 15),
        Meal("Grilled Chicken Salad" if not is_veg else "Tofu Salad", ["Chicken Breast" if not is_veg else "Firm Tofu", "Mixed Greens", "Avocado", "Balsamic"], 400, 35, 15, 20),
        Meal("Whole Wheat Wrap", ["Whole Wheat Tortilla", "Hummus", "Spinach", "Bell Peppers"], 380, 12, 55, 10)
    ]
    
    d_options = [
        Meal("Baked Salmon & Asparagus" if not is_veg else "Lentil Curry", ["Salmon" if not is_veg else "Lentils", "Asparagus", "Brown Rice"], 500, 40, 45, 18),
        Meal("Turkey Chili" if not is_veg else "Bean Chili", ["Lean Turkey" if not is_veg else "Kidney Beans", "Tomatoes", "Onions", "Spices"], 450, 35, 50, 12),
        Meal("Stir Fry", ["Broccoli", "Carrots", "Snap Peas", "Tofu" if is_veg else "Shrimp", "Soy Sauce"], 380, 25, 40, 10)
    ]
    
    s_options = [
        Meal("Apple & Peanut Butter", ["Apple", "Peanut Butter"], 200, 6, 25, 10),
        Meal("Handful of Almonds", ["Almonds"], 160, 6, 6, 14),
        Meal("Protein Shake", ["Protein Powder", "Water"], 120, 25, 3, 1)
    ]
    
    breakfast = random.choice(b_options)
    lunch = random.choice(l_options)
    dinner = random.choice(d_options)
    snack = random.choice(s_options)
    
    # Scale calories slightly to match target (simplified logic)
    current_total = breakfast.calories + lunch.calories + dinner.calories + snack.calories
    scale = target_calories / current_total if current_total > 0 else 1
    
    breakfast.calories = int(breakfast.calories * scale)
    lunch.calories = int(lunch.calories * scale)
    dinner.calories = int(dinner.calories * scale)
    snack.calories = int(snack.calories * scale)
    
    # 6. Grocery List
    all_items = set(breakfast.items + lunch.items + dinner.items + snack.items)
    grocery_list = [
        GroceryItem(name=item, category="General", bigbasket_url=_generate_bigbasket_url(item))
        for item in all_items
    ]
    
    return NutritionPlan(
        goal=fitness_goal,
        daily_calories=target_calories,
        hydration_liters=hydration_liters,
        macros=macros,
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner,
        snacks=[snack],
        grocery_list=grocery_list
    )

def to_dict(plan: NutritionPlan) -> dict:
    return {
        "goal": plan.goal,
        "daily_calories": plan.daily_calories,
        "hydration_liters": plan.hydration_liters,
        "macros": {
            "protein_g": plan.macros.protein_g,
            "carbs_g": plan.macros.carbs_g,
            "fat_g": plan.macros.fat_g
        },
        "breakfast": {
            "name": plan.breakfast.name,
            "items": plan.breakfast.items,
            "calories": plan.breakfast.calories,
            "protein_g": plan.breakfast.protein_g,
            "carbs_g": plan.breakfast.carbs_g,
            "fat_g": plan.breakfast.fat_g
        },
        "lunch": {
            "name": plan.lunch.name,
            "items": plan.lunch.items,
            "calories": plan.lunch.calories,
            "protein_g": plan.lunch.protein_g,
            "carbs_g": plan.lunch.carbs_g,
            "fat_g": plan.lunch.fat_g
        },
        "dinner": {
            "name": plan.dinner.name,
            "items": plan.dinner.items,
            "calories": plan.dinner.calories,
            "protein_g": plan.dinner.protein_g,
            "carbs_g": plan.dinner.carbs_g,
            "fat_g": plan.dinner.fat_g
        },
        "snacks": [
            {
                "name": s.name,
                "items": s.items,
                "calories": s.calories,
                "protein_g": s.protein_g,
                "carbs_g": s.carbs_g,
                "fat_g": s.fat_g
            } for s in plan.snacks
        ],
        "grocery_list": [
            {
                "name": g.name,
                "category": g.category,
                "bigbasket_url": g.bigbasket_url
            } for g in plan.grocery_list
        ]
    }
