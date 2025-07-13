# app.py

import streamlit as st
import pandas as pd
import base64
import pdfkit
import streamlit.components.v1 as components
from input_handler import validate_user_input
from filter_engine import load_dataset, apply_all_filters
from recommender import recommend_meals_by_type, get_most_similar

# Page config
st.set_page_config(page_title="🍽️ Nutrition Coach", layout="wide")

# Set background image
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('data:image/jpg;base64,{encoded}');
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_background("image/background.jpg")

# Form styling
st.markdown(
    """
    <style>
    div[data-testid="stForm"] > div:first-child {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Layout columns
spacer, left_col, right_col, spacer2 = st.columns([0.4, 1.6, 2.0, 0.4])

# Initialize session state
if "plan_html" not in st.session_state:
    st.session_state.plan_html = None
if "report_html" not in st.session_state:
    st.session_state.report_html = None

# User input form
with right_col:
    with st.form("user_input_form"):
        st.markdown("<h1>🥗 Personalized Nutrition Coach</h1>", unsafe_allow_html=True)
        st.markdown("<h5>📝 Fill in your profile to get tailored meal suggestions</h5>", unsafe_allow_html=True)

        # Personal Info
        col1, col2, col3 = st.columns(3)
        age = col1.number_input("Age", min_value=1, max_value=120, value=30)
        weight = col2.number_input("Weight (kg)", min_value=20, max_value=200, value=65)
        height = col3.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        activity_level = st.selectbox("Physical Activity Level", [
            "Sedentary (little or no exercise)",
            "Lightly active (light exercise 1–3 days/week)",
            "Moderately active (moderate exercise 3–5 days/week)",
            "Very active (hard exercise 6–7 days/week)",
            "Super active (twice a day or intense training)",
        ])
        goal = st.selectbox("Goal", ["Lose Weight", "Maintain Weight", "Gain Weight"])

        # Health Conditions
        st.markdown("#### 🏥 Health Conditions")
        health_conditions = st.multiselect(
            "Any medical conditions:",
            ["diabetes", "cholesterol", "hypertension"]
        )

        # Food Allergies
        st.markdown("#### ❗ Food Allergies")
        allergies = st.multiselect(
            "Do you have any food allergies?",
            ["nuts", "gluten", "lactose", "soy", "eggs"]
        )

        # Dietary Preferences
        st.markdown("#### 🥦 Dietary Preferences")
        dietary_preferences = st.multiselect(
            "Choose your dietary preferences:",
            ["vegan", "gluten-free"]
        )

        # Nutrition Goals
        st.markdown("#### 💡 Nutrition Goals")
        nutrition_goals = st.multiselect(
            "Select your nutritional goals:",
            ["low-calorie", "high-protein", "high-fiber", "low-fat"]
        )

        # Meals Selection
        st.markdown("#### 🍽️ Meals you want")
        meals_selected = st.multiselect(
            "Which meals do you want recommendations for?",
            ["breakfast", "lunch", "dinner"],
            default=["breakfast", "lunch", "dinner"]
        )
        num_meals_per_type = st.slider(
            "How many meal suggestions per type would you like?",
            1, 5, 2
        )

        submitted = st.form_submit_button("🔍 Get Meal Plan")

# Process form submission
if submitted:
    # Compute BMI
    bmi = weight / ((height / 100) ** 2)
    bmi_status = (
        "Underweight" if bmi < 18.5 else
        "Normal weight" if bmi < 25 else
        "Overweight" if bmi < 30 else
        "Obese"
    )
    # Compute TDEE & calories
    activity_map = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (light exercise 1–3 days/week)": 1.375,
        "Moderately active (moderate exercise 3–5 days/week)": 1.55,
        "Very active (hard exercise 6–7 days/week)": 1.725,
        "Super active (twice a day or intense training)": 1.9,
    }
    base_tdee = ((10 * weight + 6.25 * height - 5 * age) +
                 (5 if gender == "Male" else -161)) * activity_map[activity_level]
    calories = (base_tdee - 500 if goal == "Lose Weight"
                else base_tdee + 300 if goal == "Gain Weight"
                else base_tdee)

    # Build user profile
    user_profile = {
        "age": age,
        "weight": weight,
        "height": height,
        "gender": gender,
        "activity_level": activity_level,
        "goal": goal,
        "health_conditions": health_conditions,
        "dietary_preferences": dietary_preferences,
        "allergies": allergies,
        "nutrition_goals": nutrition_goals,
        "meals_selected": meals_selected,
        "num_meals_per_type": num_meals_per_type
    }

    try:
        validate_user_input(user_profile)
        df = load_dataset("data/meals.csv")
        filtered_df = apply_all_filters(df, user_profile)
        meal_plan = recommend_meals_by_type(filtered_df, user_profile, num_meals_per_type)

        # Fallback
        if all(len(v) == 0 for v in meal_plan.values()):
            fallback = user_profile.copy()
            fallback["nutrition_goals"] = []
            fallback["allergies"] = []
            filtered_df = apply_all_filters(df, fallback)
            meal_plan = recommend_meals_by_type(filtered_df, fallback, num_meals_per_type)

        # a) Health Summary HTML
        health_summary_html = f"""
        <div style='
                font-family: Inter, sans-serif;
                background: rgba(255,255,255,0.85);
                border-radius:20px;
                padding:25px;
                margin-bottom:20px;
        '>
          <h3>📁 Health Summary</h3>
            <ul style='list-style:none;padding:0;'>
                <li><b>🔹 BMI:</b> {bmi:.1f} ({bmi_status})</li>
                <li><b>🔥 Daily Calories Needed:</b> {int(calories)} kcal</li>
                <li><b>🎯 Goal:</b> {goal}</li>
                <li><b>🏃‍♀️ Activity:</b> {activity_level}</li>
                <li><b>🩺 Conditions:</b> {', '.join(health_conditions) or 'None'}</li>
                <li><b>🥦 Preferences:</b> {', '.join(dietary_preferences) or 'None'}</li>
                <li><b>📌 Nutrition Goals:</b> {', '.join(nutrition_goals) or 'None'}</li>
            </ul>
        </div>
        """

        # b) Meal Plan HTML
        plan_html = f"""
          <div style='
          font-family: Inter, sans-serif;
          background: rgba(255,255,255,0.85);
          border-radius:20px;
          padding:25px;
          margin-top:20px;
          box-shadow:0 8px 32px rgba(31,38,135,0.37);
          backdrop-filter:blur(8px);
         '>
         <h3>🍽️ Your Personalized Meal Plan</h3>
        """
        for idx, mtype in enumerate(meals_selected):
            items = meal_plan.get(mtype, [])
            plan_html += f"<h5>🍽️ {mtype.capitalize()}</h5>"
            if items:
                for meal in items:
                    plan_html += f"""
                        <div style='margin-bottom:20px;'>
                            <b>{meal['name']}</b><br>
                            <span style='color:gray;'>Tags: <code>{meal['tags']}</code></span><br><br>
                            🥕 <b>Sugar (per100g):</b> {meal['sugar_g_per100g']:.1f} g &nbsp;&nbsp;
                            💖 <b>Cholesterol (per100g):</b> {meal['cholesterol_mg_per100g']:.1f} mg &nbsp;&nbsp;
                            🔥 <b>Calories (per100g):</b> {meal['calories_per100g']:.1f} kcal<br>
                            💪 <b>Protein (per100g):</b> {meal['protein_g_per100g']:.1f} g &nbsp;&nbsp;
                            🌾 <b>Fiber (per100g):</b> {meal['fiber_g_per100g']:.1f} g &nbsp;&nbsp;
                            🧈 <b>Fat (per100g):</b> {meal['fat_g_per100g']:.1f} g<br>
                            <p style='font-size:13px;color:#444;'><i>Why this meal?</i> → {meal['reason']}</p>
                            <p style='font-size:13px;color:#444;'><i>Recipe:</i> {meal.get('recipe', 'N/A')}</p>

                        </div>
                    """
            else:
                # Enhanced fallback: show full details of most similar
                sim_name = get_most_similar(df, mtype)
                sim_row = df[df['name'] == sim_name].iloc[0]
                # compute per100g
                ratio = 100 / sim_row['serving_size_g']
                sugar = sim_row['sugar_g'] * ratio
                chol = sim_row['cholesterol_mg'] * ratio
                cal = sim_row['calories'] * ratio
                prot = sim_row['protein_g'] * ratio
                fib  = sim_row['fiber_g'] * ratio
                fat  = sim_row['fat_g'] * ratio
                plan_html += f"""
                    <div style='margin-bottom:20px;'>
                        <b>{sim_row['name']}</b><br>
                        <span style='color:gray;'>Tags: <code>{sim_row['tags']}</code></span><br><br>
                        🥕 <b>Sugar (per100g):</b> {sugar:.1f} g &nbsp;&nbsp;
                        💖 <b>Cholesterol (per100g):</b> {chol:.1f} mg &nbsp;&nbsp;
                        🔥 <b>Calories (per100g):</b> {cal:.1f} kcal<br>
                        💪 <b>Protein (per100g):</b> {prot:.1f} g &nbsp;&nbsp;
                        🌾 <b>Fiber (per100g):</b> {fib:.1f} g &nbsp;&nbsp;
                        🧈 <b>Fat (per100g):</b> {fat:.1f} g<br>
                        <p style='font-size:13px;color:#444;'><i>Why this meal?</i> → Matched closest profile</p>
                    </div>
                """
            # separator
            if idx < len(meals_selected) - 1:
                plan_html += "<hr style='border:1px solid rgba(0,0,0,0.1); margin:20px 0;'>"
        plan_html += "</div>"

        # c) Report HTML (same as before)
        report_html = f"""
            <h2>📁 Personalized Nutrition Report</h2>
            <p><b>BMI:</b> {bmi:.1f} ({bmi_status})<br>
            <b>Daily Calories:</b> {int(calories)} kcal<br><b>Goal:</b> {goal}<br>
            <b>Activity:</b> {activity_level}<br>
            <b>Conditions:</b> {', '.join(health_conditions) or 'None'}<br>
            <b>Preferences:</b> {', '.join(dietary_preferences) or 'None'}<br>
            <b>Nutrition Goals:</b> {', '.join(nutrition_goals) or 'None'}</p><hr>
        """
        for mtype, meals in meal_plan.items():
            report_html += f"<h3>{mtype.capitalize()}</h3><ul>"
            for meal in meals:
                report_html += f"""
                    <li><b>{meal['name']}</b> ({meal['tags']})<br>
                        Calories/100g: {meal['calories_per100g']:.1f} kcal,<br>
                        Protein: {meal['protein_g_per100g']:.1f} g,<br>
                        Fat: {meal['fat_g_per100g']:.1f} g,<br>
                        Sugar: {meal['sugar_g_per100g']:.1f} g,<br>
                        Fiber: {meal['fiber_g_per100g']:.1f} g,<br>
                        Cholesterol: {meal['cholesterol_mg_per100g']:.1f} mg<br>
                        Reason: {meal['reason']}
                    </li><br>
                """
            report_html += "</ul>"

        # save to session
        st.session_state.plan_html = health_summary_html + plan_html
        st.session_state.report_html = report_html

    except Exception as e:
        st.error(f"❌ Error while processing meal data: {e}")

# Display left column
with left_col:
    if st.session_state.plan_html:
        components.html(
            st.session_state.plan_html,
            height=800,
            scrolling=True
        )
        if st.button("📅 Download Nutrition Report as PDF"):
            try:
                config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
                pdf_bytes = pdfkit.from_string(
                    st.session_state.report_html,
                    False,
                    configuration=config
                )
                st.download_button(
                    label="⬇️ Click here to download PDF",
                    data=pdf_bytes,
                    file_name="nutrition_report.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"❌ PDF creation failed: {e}")