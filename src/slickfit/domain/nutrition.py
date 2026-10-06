"""Non-clinical nutrition guidance and Indian regional meal suggestion engine.

Applies strict allergy exclusions and dietary preferences with transparent limitations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

NUTRITION_ALGORITHM_VERSION = "slickfit_nut_v1"

INDIAN_MEAL_IDEAS = {
    "vegetarian": {
        "south_indian": [
            {"meal": "Breakfast", "idea": "Ragi idli or vegetable upma with sambar & mint-coconut chutney", "protein_source": "Lentils/Sambar, Ragi"},
            {"meal": "Lunch", "idea": "Brown rice with dal/rasam, mixed vegetable poriyal, and curd/paneer", "protein_source": "Dal, Curd/Paneer"},
            {"meal": "Dinner", "idea": "Foxtail millet dosa with moong dal kootu and steamed greens", "protein_source": "Moong Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Banana with roasted chana / buttermilk", "protein_source": "Roasted Chana, Buttermilk"},
        ],
        "north_indian": [
            {"meal": "Breakfast", "idea": "Besan chilla with grated paneer and coriander mint chutney", "protein_source": "Besan, Paneer"},
            {"meal": "Lunch", "idea": "Multigrain roti with rajma/chole, mixed vegetable sabzi, and raita", "protein_source": "Rajma/Chole, Raita"},
            {"meal": "Dinner", "idea": "Khichdi (moong dal & brown rice) with roasted papad and spinach curry", "protein_source": "Moong Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Dates with warm spiced milk / dry fruit sattu drink", "protein_source": "Sattu, Milk"},
        ],
    },
    "eggetarian": {
        "south_indian": [
            {"meal": "Breakfast", "idea": "Egg appam or boiled eggs with whole wheat toast & coconut milk stew", "protein_source": "Eggs"},
            {"meal": "Lunch", "idea": "Egg biryani/pulao with cucumber onion raita and sprouted moong salad", "protein_source": "Eggs, Sprouts"},
            {"meal": "Dinner", "idea": "Whole wheat parotta/roti with South Indian egg curry", "protein_source": "Eggs"},
            {"meal": "Pre/Post Run Snack", "idea": "Boiled egg chaat or banana peanut shake", "protein_source": "Eggs"},
        ],
        "north_indian": [
            {"meal": "Breakfast", "idea": "Masala egg bhurji with whole wheat paratha & herbal chai", "protein_source": "Eggs"},
            {"meal": "Lunch", "idea": "Egg curry with jeera brown rice and cucumber tomato kachumber", "protein_source": "Eggs"},
            {"meal": "Dinner", "idea": "Stuffed paneer & egg roll on whole wheat chapati with mint chutney", "protein_source": "Eggs, Paneer"},
            {"meal": "Pre/Post Run Snack", "idea": "Hard boiled eggs with roasted makhana", "protein_source": "Eggs"},
        ],
    },
    "non_vegetarian": {
        "south_indian": [
            {"meal": "Breakfast", "idea": "Steamed idlis with chicken keema / egg white omelet and vegetable sambar", "protein_source": "Chicken/Eggs"},
            {"meal": "Lunch", "idea": "Grilled/steamed fish curry with red matta rice and stir-fried beans", "protein_source": "Fish"},
            {"meal": "Dinner", "idea": "Chicken chettinad with whole wheat chapati and cucumber salad", "protein_source": "Chicken"},
            {"meal": "Pre/Post Run Snack", "idea": "Boiled eggs or homemade chicken clear soup", "protein_source": "Eggs/Chicken"},
        ],
        "north_indian": [
            {"meal": "Breakfast", "idea": "Chicken mince stuffed paratha or masala omelet with toast", "protein_source": "Chicken/Eggs"},
            {"meal": "Lunch", "idea": "Tandoori/curry chicken with whole wheat roti, yellow dal, and green salad", "protein_source": "Chicken, Dal"},
            {"meal": "Dinner", "idea": "Pan-seared spiced fish with brown rice and mixed greens", "protein_source": "Fish"},
            {"meal": "Pre/Post Run Snack", "idea": "Hard boiled eggs or sattu buttermilk", "protein_source": "Eggs"},
        ],
    },
    "vegan": {
        "south_indian": [
            {"meal": "Breakfast", "idea": "Steamed ragi puttu with kadala (black chickpea) curry", "protein_source": "Black Chickpeas, Ragi"},
            {"meal": "Lunch", "idea": "Brown rice with spinach dal, roasted soy chunks, and vegetable thoran", "protein_source": "Dal, Soya"},
            {"meal": "Dinner", "idea": "Moong dal dosa (pesarattu) with ginger chutney and stir-fried greens", "protein_source": "Moong Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted chana with fresh tender coconut water", "protein_source": "Roasted Chana"},
        ],
        "north_indian": [
            {"meal": "Breakfast", "idea": "Tofu & vegetable poha with roasted peanuts & lemon juice", "protein_source": "Tofu, Peanuts"},
            {"meal": "Lunch", "idea": "Soya bean & vegetable pulao with yellow dal tadka and beetroot salad", "protein_source": "Soya, Dal"},
            {"meal": "Dinner", "idea": "Roti with kala chana masala and steamed broccoli/spinach", "protein_source": "Kala Chana"},
            {"meal": "Pre/Post Run Snack", "idea": "Sattu water with roasted lotus seeds (makhana)", "protein_source": "Sattu"},
        ],
    },
}

ALLERGEN_KEYWORDS = {
    "peanuts": ["peanut", "peanuts", "groundnut", "groundnuts", "mungfali"],
    "tree_nuts": ["almond", "almonds", "cashew", "cashews", "walnut", "walnuts", "badam", "kaju", "pista", "pistachio", "nut", "nuts", "dry fruit"],
    "dairy": ["curd", "paneer", "milk", "raita", "buttermilk", "ghee", "cheese", "dahi", "butter", "cream", "lactose", "chaas"],
    "gluten": ["wheat", "roti", "paratha", "parotta", "toast", "bread", "atta", "maida", "chapati", "semolina", "sooji", "suji"],
    "eggs": ["egg", "eggs", "omelet", "bhurji", "anda"],
    "fish": ["fish", "prawn", "seafood", "shellfish", "crab", "shrimp", "salmon", "pomfret", "surmai", "rohu"],
    "shellfish": ["shellfish", "prawn", "prawns", "shrimp", "shrimps", "crab", "crabs", "lobster", "seafood"],
    "soy": ["soya", "soy", "tofu", "edamame"],
}


@dataclass
class NutritionAdvice:
    dietary_pattern: str
    regional_preference: str
    min_kcal: int
    max_kcal: int
    protein_g_min: int
    protein_g_max: int
    carbs_g_min: int
    carbs_g_max: int
    fats_g_min: int
    fats_g_max: int
    hydration_liters: float
    meal_ideas: list[dict[str, Any]]
    rationale: str
    limitations: str


def generate_daily_nutrition_guidance(
    dietary_pattern: str = "vegetarian",
    regional_preference: str = "south_indian",
    allergies: Optional[list[str]] = None,
    training_demand_type: str = "easy_run",  # "easy_run" | "long_run" | "rest"
    weight_kg: Optional[float] = None,
) -> NutritionAdvice:
    """Generate non-clinical Indian nutrition guidance with strict allergy filtering."""
    pattern = dietary_pattern.strip().lower()
    if pattern not in INDIAN_MEAL_IDEAS:
        pattern = "vegetarian"

    region = regional_preference.strip().lower()
    if region not in ("south_indian", "north_indian"):
        region = "south_indian"

    allergies_list = [a.strip().lower() for a in (allergies or []) if a.strip()]

    # Estimated broad caloric and macro bands based on training day
    w = weight_kg or 65.0
    if training_demand_type == "long_run":
        min_kcal = int(w * 32)
        max_kcal = int(w * 38)
        protein_g_min = int(w * 1.3)
        protein_g_max = int(w * 1.6)
        carbs_g_min = int(w * 4.5)
        carbs_g_max = int(w * 6.0)
        fats_g_min = int(w * 0.8)
        fats_g_max = int(w * 1.1)
        hydration = 3.5
        rationale = "Higher carbohydrate fueling and elevated hydration recommended for long aerobic endurance demands."
    elif training_demand_type == "rest":
        min_kcal = int(w * 26)
        max_kcal = int(w * 30)
        protein_g_min = int(w * 1.2)
        protein_g_max = int(w * 1.4)
        carbs_g_min = int(w * 3.0)
        carbs_g_max = int(w * 4.0)
        fats_g_min = int(w * 0.8)
        fats_g_max = int(w * 1.0)
        hydration = 2.5
        rationale = "Rest day nutrition focused on baseline protein repair, micronutrient density, and tissue recovery."
    else:  # easy_run / standard
        min_kcal = int(w * 28)
        max_kcal = int(w * 33)
        protein_g_min = int(w * 1.2)
        protein_g_max = int(w * 1.5)
        carbs_g_min = int(w * 3.5)
        carbs_g_max = int(w * 4.8)
        fats_g_min = int(w * 0.8)
        fats_g_max = int(w * 1.0)
        hydration = 3.0
        rationale = "Balanced aerobic training nutrition with steady complex carbohydrates and distributed protein."

    # Fetch meal ideas and filter allergens
    raw_meals = INDIAN_MEAL_IDEAS[pattern][region]
    filtered_meals: list[dict[str, Any]] = []

    for item in raw_meals:
        idea_text = item["idea"].lower()
        has_allergen = False

        for allergen in allergies_list:
            keywords = ALLERGEN_KEYWORDS.get(allergen, [allergen])
            if any(kw in idea_text for kw in keywords):
                has_allergen = True
                break

        if not has_allergen:
            filtered_meals.append(item)
        else:
            # Provide safe allergen-free replacement
            filtered_meals.append({
                "meal": item["meal"],
                "idea": "Allergen-free alternative: Steamed rice/millets with plain yellow dal & steamed greens",
                "protein_source": "Moong Dal / Millets",
            })

    limitations = (
        "Estimated general guidance only. Not medical or clinical nutrition advice. "
        "Always consult a registered sports dietitian or physician for personalized dietary prescriptions."
    )

    return NutritionAdvice(
        dietary_pattern=pattern,
        regional_preference=region,
        min_kcal=min_kcal,
        max_kcal=max_kcal,
        protein_g_min=protein_g_min,
        protein_g_max=protein_g_max,
        carbs_g_min=carbs_g_min,
        carbs_g_max=carbs_g_max,
        fats_g_min=fats_g_min,
        fats_g_max=fats_g_max,
        hydration_liters=hydration,
        meal_ideas=filtered_meals,
        rationale=rationale,
        limitations=limitations,
    )
