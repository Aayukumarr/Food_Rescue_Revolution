"""
Food Rescue ML - Scikit-Learn Benchmark Pipeline
Standard Scikit-Learn & Pandas script for academic project defense.
Run with:
    pip install scikit-learn pandas
    python3 train_sklearn.py
"""

try:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
    import time
except ImportError:
    print("scikit-learn or pandas is not installed. Run `pip install scikit-learn pandas`.")
    print("Or run the zero-dependency script: `python3 train_model.py`.")
    exit(0)

def main():
    print("=" * 65)
    print("🎓 SCIKIT-LEARN BENCHMARK PIPELINE")
    print("=" * 65)

    df = pd.read_csv('dataset.csv')
    print(f"Loaded dataset: {df.shape}")

    features = ['category', 'food_type', 'ambient_temp_c', 'humidity_percent',
                'storage_condition', 'packaging_type', 'prepared_hours_ago']
    X = pd.get_dummies(df[features], drop_first=False)
    y = df['remaining_shelf_life_hours']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 1. Random Forest Regressor
    rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    print("\n📈 RANDOM FOREST REGRESSOR EVALUATION:")
    print(f"  • R² Score: {r2 * 100:.2f}%")
    print(f"  • RMSE:     {rmse:.3f} hrs")
    print(f"  • MAE:      {mae:.3f} hrs")

if __name__ == '__main__':
    main()
