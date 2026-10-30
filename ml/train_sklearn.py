"""
Food Rescue Revolution - Academic Scikit-Learn Pipeline
Standard Python ML implementation using scikit-learn & pandas for college project evaluation.
Run with:
    pip install scikit-learn pandas
    python3 ml/train_sklearn.py
"""

try:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, classification_report
    import json
    import time
except ImportError:
    print("Notice: 'scikit-learn' or 'pandas' not installed in this environment.")
    print("Run `python3 ml/train_model.py` which uses the built-in pure Python ML engine.")
    exit(0)

def main():
    print("=" * 65)
    print("🎓 SCICAT-LEARN FOOD RESCUE SHELF-LIFE PREDICTOR")
    print("=" * 65)

    df = pd.read_csv('ml/dataset.csv')
    print(f"Dataset shape: {df.shape}")

    # Feature engineering & One-Hot Encoding
    features = ['category', 'food_type', 'ambient_temp_c', 'humidity_percent',
                'storage_condition', 'packaging_type', 'prepared_hours_ago']
    X = pd.get_dummies(df[features], drop_first=False)
    y_reg = df['remaining_shelf_life_hours']
    y_clf = df['urgency_tier']

    X_train, X_test, y_train, y_test, clf_train, clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, random_state=42
    )

    # 1. Random Forest Regressor
    rf_reg = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    rf_reg.fit(X_train, y_train)
    y_pred = rf_reg.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    print("\n📈 REGRESSION EVALUATION METRICS:")
    print(f"  • R² Score: {r2 * 100:.2f}%")
    print(f"  • RMSE:     {rmse:.3f} hrs")
    print(f"  • MAE:      {mae:.3f} hrs")

    # 2. Gradient Boosting Classifier for Urgency
    gb_clf = GradientBoostingClassifier(n_estimators=60, max_depth=4, random_state=42)
    gb_clf.fit(X_train, clf_train)
    clf_pred = gb_clf.predict(X_test)

    print("\n🎯 CLASSIFICATION REPORT (Urgency Tier):")
    print(classification_report(clf_test, clf_pred))

if __name__ == '__main__':
    main()
