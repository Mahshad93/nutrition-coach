def get_user_input():
    # Test profile with all expected keys
    user_profile = {
        "age": 30,
        "weight": 70,
        "height": 165,
        "gender": "Female",
        "activity_level": "Lightly active (light exercise 1-3 days/week)",
        "goal": "Lose Weight",
        "health_conditions": ["diabetes"],
        "dietary_preferences": ["vegan"],
        "allergies": ["gluten"],
        "nutrition_goals": ["low-calorie", "high-protein"],
        "meals_selected": ["breakfast", "lunch", "dinner"],
        "num_meals_per_type": 2  # ✅ اضافه شد
    }
    return user_profile

def validate_user_input(profile):
    # Basic numeric checks
    if profile["age"] <= 0 or profile["weight"] <= 0 or profile["height"] <= 0:
        raise ValueError("Age, weight, and height must be positive numbers.")

    # Type checks for list fields
    for field in ["health_conditions", "dietary_preferences", "allergies", "nutrition_goals", "meals_selected"]:
        if not isinstance(profile.get(field, []), list):
            raise TypeError(f"{field} must be a list.")

    # Optional: check gender, activity_level, goal presence
    if profile.get("gender") not in ["Female", "Male", "Other"]:
        raise ValueError("Gender must be Female, Male, or Other.")
    
    if "activity_level" not in profile or not isinstance(profile["activity_level"], str):
        raise ValueError("Activity level must be provided.")

    if "goal" not in profile or profile["goal"] not in ["Lose Weight", "Maintain Weight", "Gain Weight"]:
        raise ValueError("Goal must be one of the predefined options.")
    
    # ✅ بررسی مقدار انتخاب‌شده برای تعداد وعده‌ها
    if "num_meals_per_type" in profile:
        if not isinstance(profile["num_meals_per_type"], int) or not (1 <= profile["num_meals_per_type"] <= 5):
            raise ValueError("num_meals_per_type must be an integer between 1 and 5.")

    return True

# Test block
if __name__ == "__main__":
    user = get_user_input()
    if validate_user_input(user):
        print("✅ User input is valid:")
        print(user)
