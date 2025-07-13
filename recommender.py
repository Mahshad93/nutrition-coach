# recommender.py

import pandas as pd
import numpy as np

def recommend_meals_by_type(df: pd.DataFrame, user_profile: dict, num_meals_per_type: int = 1) -> dict:
    """
    Recommend meals by meal type with reasoning and nutrition per 100g.

    Parameters:
        df (pd.DataFrame): Filtered meals DataFrame.
        user_profile (dict): Includes goals, preferences, conditions.
        num_meals_per_type (int): Number of meals to return per type.

    Returns:
        dict: meal_type -> list of recommended meals with details.
    """
    recommended = {}
    nutrition_goals = user_profile.get("nutrition_goals", [])
    dietary_preferences = user_profile.get("dietary_preferences", [])
    conditions = user_profile.get("health_conditions", [])

    for meal_type in df["meal_type"].unique():
        meals_for_type = df[df["meal_type"] == meal_type]
        if meals_for_type.empty:
            continue

        # Randomly sample up to the requested number of meals
        sampled = meals_for_type.sample(n=min(num_meals_per_type, len(meals_for_type)))

        # Add nutritional info per 100g
        for col in ['calories', 'protein_g', 'fat_g', 'fiber_g', 'sugar_g', 'sodium_mg', 'cholesterol_mg']:
            sampled[f'{col}_per100g'] = (sampled[col] / sampled['serving_size_g']) * 100

        # Build an explanation string
        reasons = []
        if "low-calorie" in nutrition_goals:
            reasons.append("low in calories")
        if "high-protein" in nutrition_goals:
            reasons.append("high in protein")
        if "high-fiber" in nutrition_goals:
            reasons.append("high in fiber")
        if "low-fat" in nutrition_goals:
            reasons.append("low in fat")
        if "vegan" in dietary_preferences:
            reasons.append("vegan-friendly")
        if "gluten-free" in dietary_preferences:
            reasons.append("gluten-free")
        if "diabetes" in conditions:
            reasons.append("suitable for diabetes")
        if "cholesterol" in conditions:
            reasons.append("low cholesterol")
        if "hypertension" in conditions:
            reasons.append("low sodium")

        sampled["reason"] = ", ".join(reasons) or "Matched your profile"

        # Convert DataFrame to list of dicts for Streamlit rendering
        recommended[meal_type] = sampled.to_dict(orient="records")

    return recommended


def get_most_similar(df: pd.DataFrame, meal_type: str, target: dict = None) -> str:
    """
    Find the most similar meal of a given type, based on Euclidean distance
    over nutrition columns.

    Parameters:
        df (pd.DataFrame): The full meals DataFrame.
        meal_type (str): Which meal_type to search.
        target (dict, optional): If provided, dict of target values for
                                 ['calories','protein_g','fat_g','fiber_g','sugar_g'].
                                 If None, use the mean of that meal_type.

    Returns:
        str: Name of the closest matching meal.
    """
    subset = df[df["meal_type"] == meal_type]
    if subset.empty:
        return "No available options"

    cols = ["calories", "protein_g", "fat_g", "fiber_g", "sugar_g"]
    data = subset[cols].values

    if target:
        target_vals = np.array([target.get(c, subset[c].mean()) for c in cols])
    else:
        target_vals = subset[cols].mean().values

    # Compute Euclidean distances
    dists = np.linalg.norm(data - target_vals, axis=1)
    idx = dists.argmin()

    return subset.iloc[idx]["name"]
