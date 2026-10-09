"""Non-clinical nutrition guidance and Indian regional meal suggestion engine.

Applies strict allergy exclusions and dietary preferences with transparent limitations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

NUTRITION_ALGORITHM_VERSION = "slickfit_nut_v1"

INDIAN_MEAL_IDEAS: dict[str, dict[str, list[dict[str, str]]]] = {
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
        "west_indian": [
            {"meal": "Breakfast", "idea": "Methi thepla with curd or steamed nylon khaman dhokla", "protein_source": "Curd, Besan"},
            {"meal": "Lunch", "idea": "Gujarati/Maharashtrian sprouted usal with multigrain bhakri and cucumber koshimbir", "protein_source": "Sprouts, Moong"},
            {"meal": "Dinner", "idea": "Bajra khichdi with mixed vegetable kadhi and steamed green beans", "protein_source": "Kadhi, Bajra"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted makhana and dry coconut with jaggery", "protein_source": "Makhana"},
        ],
        "east_indian": [
            {"meal": "Breakfast", "idea": "Chire bhaja with boiled sprouts / sattu sherbet", "protein_source": "Sattu, Sprouts"},
            {"meal": "Lunch", "idea": "Brown rice with traditional Odia/Bengali dalma (lentils & raw papaya) and labra", "protein_source": "Dalma Lentils"},
            {"meal": "Dinner", "idea": "Whole wheat roti with ghugni (yellow pea curry) and roasted paneer", "protein_source": "Yellow Peas, Paneer"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted chana with fresh lemon juice and cucumber", "protein_source": "Roasted Chana"},
        ],
        "central_indian": [
            {"meal": "Breakfast", "idea": "Indori poha with sprouted lentils and roasted peanuts", "protein_source": "Sprouts, Peanuts"},
            {"meal": "Lunch", "idea": "Dal bafla (steamed & baked whole wheat dumplings with mixed panchmel dal)", "protein_source": "Panchmel Dal"},
            {"meal": "Dinner", "idea": "Jowar roti with sev tamatar curry and cucumber tomato salad", "protein_source": "Jowar, Curd"},
            {"meal": "Pre/Post Run Snack", "idea": "Sprouted moong chaat with chaat masala and lemon", "protein_source": "Moong Sprouts"},
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
        "west_indian": [
            {"meal": "Breakfast", "idea": "Parsi akuri (spiced scrambled eggs) with whole wheat toast", "protein_source": "Eggs"},
            {"meal": "Lunch", "idea": "Egg kolhapuri with jowar bhakri and cucumber salad", "protein_source": "Eggs"},
            {"meal": "Dinner", "idea": "Egg pulav with Gujarati kadhi and roasted papad", "protein_source": "Eggs, Kadhi"},
            {"meal": "Pre/Post Run Snack", "idea": "Boiled eggs sprinkled with roasted cumin powder", "protein_source": "Eggs"},
        ],
        "east_indian": [
            {"meal": "Breakfast", "idea": "Dimer devil / boiled egg salad with sattu drink", "protein_source": "Eggs, Sattu"},
            {"meal": "Lunch", "idea": "Bengali dimer jhol (egg & potato curry) with brown rice", "protein_source": "Eggs"},
            {"meal": "Dinner", "idea": "Whole wheat roti with egg tadka dal and tomato salad", "protein_source": "Eggs, Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Hard boiled egg whites with roasted chana", "protein_source": "Eggs"},
        ],
        "central_indian": [
            {"meal": "Breakfast", "idea": "Egg bhurji with indori poha and green chutney", "protein_source": "Eggs"},
            {"meal": "Lunch", "idea": "Egg curry with steamed rice and yellow dal", "protein_source": "Eggs, Dal"},
            {"meal": "Dinner", "idea": "Multigrain roti with boiled egg chaat and stir-fried greens", "protein_source": "Eggs"},
            {"meal": "Pre/Post Run Snack", "idea": "Boiled eggs with salted buttermilk", "protein_source": "Eggs, Buttermilk"},
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
        "west_indian": [
            {"meal": "Breakfast", "idea": "Egg bhurji with thepla or chicken sandwich on multigrain bread", "protein_source": "Eggs, Chicken"},
            {"meal": "Lunch", "idea": "Malvani fish curry (pomfret/surmai) with steamed rice and solkadhi", "protein_source": "Fish"},
            {"meal": "Dinner", "idea": "Saoji chicken curry with jowar roti and cucumber koshimbir", "protein_source": "Chicken"},
            {"meal": "Pre/Post Run Snack", "idea": "Chicken clear broth with roasted makhana", "protein_source": "Chicken"},
        ],
        "east_indian": [
            {"meal": "Breakfast", "idea": "Boiled eggs with whole wheat toast and sattu drink", "protein_source": "Eggs, Sattu"},
            {"meal": "Lunch", "idea": "Macher jhol (Rohu/Katla fish in light mustard-cumin broth) with brown rice", "protein_source": "Fish"},
            {"meal": "Dinner", "idea": "Bengali chicken kosha with multigrain chapati and green salad", "protein_source": "Chicken"},
            {"meal": "Pre/Post Run Snack", "idea": "Fish/chicken clear soup with lemon", "protein_source": "Fish/Chicken"},
        ],
        "central_indian": [
            {"meal": "Breakfast", "idea": "Chicken keema with whole wheat pav / scrambled eggs", "protein_source": "Chicken/Eggs"},
            {"meal": "Lunch", "idea": "Country chicken curry with steamed rice and cucumber raita", "protein_source": "Chicken"},
            {"meal": "Dinner", "idea": "Bhopali murgh rezala with whole wheat roti and mixed salad", "protein_source": "Chicken"},
            {"meal": "Pre/Post Run Snack", "idea": "Boiled eggs with buttermilk", "protein_source": "Eggs"},
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
        "west_indian": [
            {"meal": "Breakfast", "idea": "Sprouted moong thepla with green mint-coriander chutney", "protein_source": "Moong Sprouts"},
            {"meal": "Lunch", "idea": "Sprouted matki usal with jowar bhakri and cucumber salad", "protein_source": "Matki Sprouts"},
            {"meal": "Dinner", "idea": "Toor dal khichdi with mixed vegetable stir fry", "protein_source": "Toor Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted peanuts and dry coconut flakes", "protein_source": "Peanuts"},
        ],
        "east_indian": [
            {"meal": "Breakfast", "idea": "Sattu sherbet with lemon juice and roasted cumin", "protein_source": "Sattu"},
            {"meal": "Lunch", "idea": "Brown rice with panch phoron dal and raw banana kofta curry", "protein_source": "Dal"},
            {"meal": "Dinner", "idea": "Whole wheat roti with yellow pea ghugni and steamed greens", "protein_source": "Yellow Peas"},
            {"meal": "Pre/Post Run Snack", "idea": "Sprouted kala chana chaat", "protein_source": "Kala Chana"},
        ],
        "central_indian": [
            {"meal": "Breakfast", "idea": "Poha with boiled green peas and sprouted moong", "protein_source": "Green Peas, Moong"},
            {"meal": "Lunch", "idea": "Dal bafla prepared with plant oil and panchmel dal", "protein_source": "Panchmel Dal"},
            {"meal": "Dinner", "idea": "Multigrain roti with soya chunk sabzi and fresh tomato cucumber salad", "protein_source": "Soya Chunks"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted chana with lemon water", "protein_source": "Roasted Chana"},
        ],
    },
    "jain": {
        "south_indian": [
            {"meal": "Breakfast", "idea": "Steamed idli/dosa with coconut-coriander chutney and no-root sambar", "protein_source": "Lentils, Moong"},
            {"meal": "Lunch", "idea": "Rice with moong dal, raw banana poriyal, and fresh curd/paneer", "protein_source": "Moong Dal, Paneer"},
            {"meal": "Dinner", "idea": "Ragi dosa with yellow dal and steamed bottle gourd", "protein_source": "Ragi, Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted chana with fresh buttermilk", "protein_source": "Chana, Buttermilk"},
        ],
        "north_indian": [
            {"meal": "Breakfast", "idea": "Moong dal chilla with fresh paneer filling and green chutney", "protein_source": "Moong Dal, Paneer"},
            {"meal": "Lunch", "idea": "Whole wheat roti with jain rajma/chole (no onion/garlic/potato) and cucumber raita", "protein_source": "Rajma, Raita"},
            {"meal": "Dinner", "idea": "Khichdi with roasted papad and bottle gourd (lauki) sabzi", "protein_source": "Moong Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Warm spiced milk with roasted makhana", "protein_source": "Milk, Makhana"},
        ],
        "west_indian": [
            {"meal": "Breakfast", "idea": "Jain thepla (methi/sprouts) with fresh curd", "protein_source": "Curd, Sprouts"},
            {"meal": "Lunch", "idea": "Jain sprouted usal with multigrain bhakri and cucumber salad", "protein_source": "Sprouts"},
            {"meal": "Dinner", "idea": "Bajra khichdi with jain kadhi (no onion/garlic)", "protein_source": "Kadhi, Bajra"},
            {"meal": "Pre/Post Run Snack", "idea": "Dry roasted makhana and crushed almonds", "protein_source": "Makhana, Almonds"},
        ],
        "east_indian": [
            {"meal": "Breakfast", "idea": "Sattu drink with roasted cumin and rock salt", "protein_source": "Sattu"},
            {"meal": "Lunch", "idea": "Rice with jain dalma (lentils & raw plantain/pumpkin) and paneer curry", "protein_source": "Lentils, Paneer"},
            {"meal": "Dinner", "idea": "Whole wheat roti with yellow pea curry and steamed green beans", "protein_source": "Yellow Peas"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted chana with buttermilk", "protein_source": "Chana"},
        ],
        "central_indian": [
            {"meal": "Breakfast", "idea": "Jain poha (no potato/onion) with sprouted moong and peanuts", "protein_source": "Moong, Peanuts"},
            {"meal": "Lunch", "idea": "Jain dal bafla with pure toor dal and curd", "protein_source": "Toor Dal, Curd"},
            {"meal": "Dinner", "idea": "Multigrain roti with jain paneer bhurji and cucumber salad", "protein_source": "Paneer"},
            {"meal": "Pre/Post Run Snack", "idea": "Sprouted moong chaat with lemon", "protein_source": "Moong Sprouts"},
        ],
    },
    "swaminarayan": {
        "south_indian": [
            {"meal": "Breakfast", "idea": "Ragi dosa with coconut coriander chutney and hing-tempered sambar", "protein_source": "Ragi, Dal"},
            {"meal": "Lunch", "idea": "Brown rice with toor dal rasam, cabbage poriyal, and fresh curd", "protein_source": "Toor Dal, Curd"},
            {"meal": "Dinner", "idea": "Pesarattu (green moong dosa) with fresh mint chutney and steamed greens", "protein_source": "Green Moong"},
            {"meal": "Pre/Post Run Snack", "idea": "Banana with roasted chana and buttermilk", "protein_source": "Chana, Buttermilk"},
        ],
        "north_indian": [
            {"meal": "Breakfast", "idea": "Besan paneer chilla with fresh coriander chutney", "protein_source": "Besan, Paneer"},
            {"meal": "Lunch", "idea": "Multigrain roti with satvik rajma/chole (no onion/garlic) and fresh raita", "protein_source": "Rajma, Raita"},
            {"meal": "Dinner", "idea": "Moong dal khichdi with ghee and spinach tomato sabzi", "protein_source": "Moong Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Warm spiced milk with dates and almonds", "protein_source": "Milk, Nuts"},
        ],
        "west_indian": [
            {"meal": "Breakfast", "idea": "Methi thepla with fresh curd and chundo", "protein_source": "Curd"},
            {"meal": "Lunch", "idea": "Swaminarayan khichdi with sweet-tangy kadhi and raw papaya sambharo", "protein_source": "Kadhi, Dal"},
            {"meal": "Dinner", "idea": "Jowar bhakri with green peas & paneer curry", "protein_source": "Paneer, Peas"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted makhana and dry dates", "protein_source": "Makhana"},
        ],
        "east_indian": [
            {"meal": "Breakfast", "idea": "Sattu drink with lemon and roasted cumin powder", "protein_source": "Sattu"},
            {"meal": "Lunch", "idea": "Rice with satvik dalma and fresh paneer bhurji", "protein_source": "Lentils, Paneer"},
            {"meal": "Dinner", "idea": "Whole wheat roti with yellow dal and steamed vegetables", "protein_source": "Yellow Dal"},
            {"meal": "Pre/Post Run Snack", "idea": "Roasted chana with fresh coconut slices", "protein_source": "Chana"},
        ],
        "central_indian": [
            {"meal": "Breakfast", "idea": "Satvik poha with roasted peanuts and green peas", "protein_source": "Peanuts, Peas"},
            {"meal": "Lunch", "idea": "Dal bafla with panchmel dal and fresh chaas", "protein_source": "Panchmel Dal, Chaas"},
            {"meal": "Dinner", "idea": "Multigrain roti with sev tamatar sabzi (satvik style) and cucumber salad", "protein_source": "Lentils/Curd"},
            {"meal": "Pre/Post Run Snack", "idea": "Sprouted moong with rock salt and lemon", "protein_source": "Moong Sprouts"},
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
    foods_avoided: Optional[list[str]] = None,
    activity_level: str = "moderate",
    intake_target_kcal: Optional[int] = None,
) -> NutritionAdvice:
    """Generate non-clinical Indian nutrition guidance with strict allergy filtering."""
    pattern = (dietary_pattern or "vegetarian").strip().lower()
    if pattern not in INDIAN_MEAL_IDEAS:
        pattern = "vegetarian"

    region = (regional_preference or "south_indian").strip().lower()
    if region not in INDIAN_MEAL_IDEAS[pattern]:
        region = "south_indian" if "south_indian" in INDIAN_MEAL_IDEAS[pattern] else list(INDIAN_MEAL_IDEAS[pattern].keys())[0]

    allergies_list = [a.strip().lower() for a in (allergies or []) if a.strip()]

    # Estimated broad caloric and macro bands based on training day
    w = weight_kg or 65.0
    activity_factor = {"low": 0.92, "moderate": 1.0, "high": 1.08}.get((activity_level or "moderate").lower(), 1.0)
    if training_demand_type == "long_run":
        min_kcal = int(w * 32 * activity_factor)
        max_kcal = int(w * 38 * activity_factor)
        protein_g_min = int(w * 1.3)
        protein_g_max = int(w * 1.6)
        carbs_g_min = int(w * 4.5)
        carbs_g_max = int(w * 6.0)
        fats_g_min = int(w * 0.8)
        fats_g_max = int(w * 1.1)
        hydration = 3.5
        rationale = "Higher carbohydrate fueling and elevated hydration recommended for long aerobic endurance demands."
    elif training_demand_type == "rest":
        min_kcal = int(w * 26 * activity_factor)
        max_kcal = int(w * 30 * activity_factor)
        protein_g_min = int(w * 1.2)
        protein_g_max = int(w * 1.4)
        carbs_g_min = int(w * 3.0)
        carbs_g_max = int(w * 4.0)
        fats_g_min = int(w * 0.8)
        fats_g_max = int(w * 1.0)
        hydration = 2.5
        rationale = "Rest day nutrition focused on baseline protein repair, micronutrient density, and tissue recovery."
    else:  # easy_run / standard
        min_kcal = int(w * 28 * activity_factor)
        max_kcal = int(w * 33 * activity_factor)
        protein_g_min = int(w * 1.2)
        protein_g_max = int(w * 1.5)
        carbs_g_min = int(w * 3.5)
        carbs_g_max = int(w * 4.8)
        fats_g_min = int(w * 0.8)
        fats_g_max = int(w * 1.0)
        hydration = 3.0
        rationale = "Balanced aerobic training nutrition with steady complex carbohydrates and distributed protein."

    if intake_target_kcal is not None:
        min_kcal = min(min_kcal, intake_target_kcal)
        max_kcal = max(min_kcal, intake_target_kcal)

    # Fetch meal ideas and filter allergens
    raw_meals = INDIAN_MEAL_IDEAS[pattern][region]
    filtered_meals: list[dict[str, Any]] = []

    for item in raw_meals:
        idea_text = item["idea"].lower()
        has_allergen = False

        excluded = allergies_list + [item.strip().lower() for item in (foods_avoided or []) if item.strip()]
        for allergen in excluded:
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
