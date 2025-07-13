# Personalized Nutrition Coach

## Overview
This project is a personalized nutrition recommendation web application built using Streamlit. It helps users receive tailored meal suggestions based on personal data, health conditions, dietary preferences, allergies, and nutritional goals.

## Features
-User Profile Input: Input form for age, weight, height, gender, activity level, and goals
- Health Conditions: Support for diabetes, high cholesterol, and hypertension filters
- Nutrition Goals: Low-calorie, high-protein, high-fiber, low-fat
- Meal Plan Generation: Rule-based filtering to produce breakfast, lunch, and dinner suggestions
- Fallback Suggestions: Alternative meals if strict filters yield no results
- Health Summary: Display BMI, daily calorie requirement, and goal summary
- PDF Report: Downloadable report of meal plan and health summary

## Folder Structure
```
.
├── app.py
├── input_handler.py
├── filter_engine.py
├── recommender.py
├── data/
│   └── meals.csv
├── image/
│   └── background.jpg
├── requirements.txt
├── Dockerfile
├── README.md
└── diagrams/
    ├── use_case.png
    └── (upcoming: bdd.png, activity.png)
```

## How to Run

### Local
Install the required Python packages:
```bash
pip install -r requirements.txt
```

Then run the app:
```bash
streamlit run app.py
```

### Docker
Build and run the Docker container:
```bash
docker build -t nutrition-coach .
docker run -p 8501:8501 nutrition-coach
```

## Output
- Meal recommendations with nutritional breakdown
- Fallback suggestions if primary results are empty
- PDF report available for download

## UML Diagrams
- Use Case Diagram: `diagrams/use_case.png`
- Block Definition Diagram: [coming soon]
- Activity Diagram: [coming soon]

## Final Documentation
To be submitted along with this README, diagrams, and PDF output examples.