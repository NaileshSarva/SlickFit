"""Unit tests for nutrition guidance, dietary preferences, and allergy filtering."""

import pytest

from src.slickfit.domain.nutrition import generate_daily_nutrition_guidance


def test_peanut_and_dairy_allergy_filtering():
    advice = generate_daily_nutrition_guidance(
        dietary_pattern="vegetarian",
        regional_preference="south_indian",
        allergies=["peanuts", "dairy"],
    )

    for meal in advice.meal_ideas:
        idea_lower = meal["idea"].lower()
        assert "paneer" not in idea_lower
        assert "curd" not in idea_lower
        assert "peanut" not in idea_lower


def test_tree_nuts_and_shellfish_allergy_filtering():
    """Verify tree nuts (badam/kaju/almonds/cashews) and shellfish (prawns/seafood) are filtered."""
    # North Indian vegetarian with tree nuts allergy
    north_veg_advice = generate_daily_nutrition_guidance(
        dietary_pattern="vegetarian",
        regional_preference="north_indian",
        allergies=["tree_nuts"],
    )
    for meal in north_veg_advice.meal_ideas:
        idea_lower = meal["idea"].lower()
        assert "dry fruit" not in idea_lower
        assert "badam" not in idea_lower
        assert "kaju" not in idea_lower

    # South Indian non-veg with shellfish allergy
    south_nonveg_advice = generate_daily_nutrition_guidance(
        dietary_pattern="non_vegetarian",
        regional_preference="south_indian",
        allergies=["shellfish"],
    )
    for meal in south_nonveg_advice.meal_ideas:
        idea_lower = meal["idea"].lower()
        assert "prawn" not in idea_lower
        assert "crab" not in idea_lower
        assert "seafood" not in idea_lower
        assert "shellfish" not in idea_lower


def test_non_clinical_disclaimer_present():
    advice = generate_daily_nutrition_guidance()
    assert "Not medical or clinical nutrition advice" in advice.limitations
    assert advice.hydration_liters >= 2.0


def test_long_run_training_demand_elevates_carbs_and_hydration():
    rest_advice = generate_daily_nutrition_guidance(training_demand_type="rest", weight_kg=70.0)
    long_advice = generate_daily_nutrition_guidance(training_demand_type="long_run", weight_kg=70.0)

    assert long_advice.min_kcal > rest_advice.min_kcal
    assert long_advice.carbs_g_max > rest_advice.carbs_g_max
    assert long_advice.hydration_liters > rest_advice.hydration_liters


def test_foods_avoided_are_filtered_and_user_kcal_target_is_used():
    advice = generate_daily_nutrition_guidance(
        dietary_pattern="vegetarian",
        regional_preference="central_indian",
        foods_avoided=["peanuts"],
        intake_target_kcal=2300,
        activity_level="high",
    )
    assert advice.min_kcal <= 2300 <= advice.max_kcal
    assert all("peanut" not in meal["idea"].lower() for meal in advice.meal_ideas)
