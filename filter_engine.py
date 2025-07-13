import pandas as pd
import numpy as np


def load_dataset(path: str = "data/meals.csv") -> pd.DataFrame:
    """Load the food dataset from CSV."""
    return pd.read_csv(path)


# ------------------ Filter Functions ------------------

def filter_by_dietary_preferences(
    df: pd.DataFrame,
    preferences: list,
    logic: str = "AND"
) -> pd.DataFrame:
    """
    Keep meals matching dietary preferences.

    logic 'AND': must match all prefs; 'OR': match any.
    """
    if not preferences:
        return df
    masks = [df["tags"].str.contains(pref, case=False, na=False) for pref in preferences]
    if logic.upper() == "AND":
        combined = np.logical_and.reduce(masks)
    else:
        combined = np.logical_or.reduce(masks)
    return df[combined]


def filter_by_health_conditions(
    df: pd.DataFrame,
    conditions: list,
    logic: str = "AND"
) -> pd.DataFrame:
    """
    Filter by health conditions. Conditions: 'diabetes', 'cholesterol', 'hypertension'.

    logic 'AND': satisfy all; 'OR': satisfy any.
    """
    if not conditions:
        return df
    masks = []
    for cond in conditions:
        if cond == "diabetes":
            masks.append(df["sugar_g"] <= 10)
        elif cond == "cholesterol":
            masks.append(df["cholesterol_mg"] <= 75)
        elif cond == "hypertension":
            masks.append(df["sodium_mg"] <= 140)
    if not masks:
        return df
    if logic.upper() == "AND":
        combined = np.logical_and.reduce(masks)
    else:
        combined = np.logical_or.reduce(masks)
    return df[combined]


def filter_by_nutrition_goals(
    df: pd.DataFrame,
    goals: list,
    logic: str = "AND"
) -> pd.DataFrame:
    """
    Filter by nutrition goals. Goals: 'low-calorie', 'high-protein', 'high-fiber', 'low-fat'.

    logic 'AND': satisfy all; 'OR': satisfy any.
    """
    if not goals:
        return df
    masks = []
    for g in goals:
        if g == "low-calorie":
            masks.append(df["calories"] <= 400)
        elif g == "high-protein":
            masks.append(df["protein_g"] >= 15)
        elif g == "high-fiber":
            masks.append(df["fiber_g"] >= 5)
        elif g == "low-fat":
            masks.append(df["fat_g"] <= 10)
    if not masks:
        return df
    if logic.upper() == "AND":
        combined = np.logical_and.reduce(masks)
    else:
        combined = np.logical_or.reduce(masks)
    return df[combined]


def filter_by_allergies(
    df: pd.DataFrame,
    allergies: list
) -> pd.DataFrame:
    """
    Exclude meals containing any of the listed allergies (OR logic).
    """
    for allergy in allergies:
        df = df[~df["tags"].str.contains(allergy, case=False, na=False)]
    return df


# ------------------ Apply All Filters ------------------

def apply_all_filters(df: pd.DataFrame, user_profile: dict) -> pd.DataFrame:
    """
    Sequentially apply filters with optional logic from user_profile:
      - dietary_preferences (AND/OR)
      - health_conditions (AND/OR)
      - nutrition_goals (AND/OR)
      - allergies (exclude any)
    """
    df_out = df.copy()
    # Dietary preferences
    df_out = filter_by_dietary_preferences(
        df_out,
        user_profile.get("dietary_preferences", []),
        user_profile.get("dietary_logic", "AND")
    )
    # Health conditions
    df_out = filter_by_health_conditions(
        df_out,
        user_profile.get("health_conditions", []),
        user_profile.get("health_logic", "AND")
    )
    # Nutrition goals
    df_out = filter_by_nutrition_goals(
        df_out,
        user_profile.get("nutrition_goals", []),
        user_profile.get("nutrition_logic", "AND")
    )
    # Allergies exclusion
    df_out = filter_by_allergies(
        df_out,
        user_profile.get("allergies", [])
    )
    return df_out


# ------------------ Test Example ------------------

if __name__ == "__main__":
    user_profile = {
        "dietary_preferences": ["vegan", "gluten-free"],
        "dietary_logic": "OR",
        "health_conditions": ["diabetes", "cholesterol"],
        "health_logic": "AND",
        "nutrition_goals": ["low-calorie", "high-protein"],
        "nutrition_logic": "OR",
        "allergies": ["nuts"]
    }
    df = load_dataset()
    print("Dietary filter:", len(apply_all_filters(df, user_profile)))
    user_profile.update({"dietary_logic":"AND", "health_logic":"OR"})
    print("Combined logic:", len(apply_all_filters(df, user_profile)))
