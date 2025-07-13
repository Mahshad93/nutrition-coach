import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

from filter_engine import apply_all_filters


def train_decision_tree(df: pd.DataFrame, user_profile: dict, max_depth: int = 5):
    """
    Train a Decision Tree classifier to predict meal suitability based on rule-based labels.

    Parameters:
        df (pd.DataFrame): Full meals dataset.
        user_profile (dict): User settings for labeling (nutrition_goals, dietary_preferences, health_conditions, allergies).
        max_depth (int): Maximum depth of the decision tree.

    Returns:
        model (DecisionTreeClassifier): Trained decision tree model.
        feature_cols (list): List of feature column names used.
    """
    # Label data via rule-based filtering
    # Meals that pass all filters are labeled 1, others 0
    filtered = apply_all_filters(df, user_profile)
    filtered_names = set(filtered['name'])

    df_labeled = df.copy()
    df_labeled['label'] = df_labeled['name'].apply(lambda n: 1 if n in filtered_names else 0)

    # Features and label
    feature_cols = ['calories', 'protein_g', 'fat_g', 'fiber_g', 'sugar_g', 'sodium_mg', 'cholesterol_mg']
    X = df_labeled[feature_cols]
    y = df_labeled['label']

    # Split for evaluation (optional)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    print(f"Decision Tree accuracy: {acc:.2f}")
    print("Confusion Matrix:")
    print(cm)

    return model, feature_cols


def recommend_with_ml(df: pd.DataFrame, user_profile: dict, k: int = 2, max_depth: int = 5):
    """
    Recommend meals per type using a trained Decision Tree classifier.

    Parameters:
        df (pd.DataFrame): Full meals dataset.
        user_profile (dict): User settings.
        k (int): Number of meals per type to recommend.
        max_depth (int): Max depth for the decision tree.

    Returns:
        dict: meal_type -> list of recommended meal dicts with probabilities.
    """
    # Train model
    model, feature_cols = train_decision_tree(df, user_profile, max_depth)

    # Predict probabilities on full dataset
    probs = model.predict_proba(df[feature_cols])[:, 1]  # probability of label=1
    df_scores = df.copy()
    df_scores['score'] = probs

    recommendations = {}
    for meal_type in df_scores['meal_type'].unique():
        subset = df_scores[df_scores['meal_type'] == meal_type]
        if subset.empty:
            recommendations[meal_type] = []
            continue
        # Sort by descending score and pick top k
        topk = subset.nlargest(k, 'score')
        # Add score to each record
        recs = topk.to_dict(orient='records')
        recommendations[meal_type] = recs

    return recommendations


# Optional test
if __name__ == '__main__':
    from filter_engine import load_dataset
    user_profile = {
        "nutrition_goals": ["low-calorie", "high-protein"],
        "dietary_preferences": ["vegan"],
        "health_conditions": ["diabetes"],
        "allergies": ["gluten"]
    }
    df = load_dataset()
    recs = recommend_with_ml(df, user_profile, k=2)
    for mtype, meals in recs.items():
        print(f"\n{mtype}:")
        for meal in meals:
            print(f"- {meal['name']} (score: {meal['score']:.2f})")
