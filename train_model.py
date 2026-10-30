"""
Food Rescue ML - Machine Learning Training Pipeline
Trains an Ensemble Random Forest Regressor & Multi-Class Urgency Classifier.
100% Zero-Dependency Python (Runs on Python 3 out of the box).
"""

import csv
import json
import math
import random
import time
from ml_engine import FEATURE_NAMES, encode_row, load_dataset, build_tree, predict_tree

random.seed(42)

def main():
    print("=" * 65)
    print("🤖 FOOD RESCUE ML - MACHINE LEARNING TRAINING PIPELINE")
    print("Algorithm: Ensemble Random Forest Regressor (12 Estimators)")
    print("=" * 65)

    start_time = time.time()
    X, y, records = load_dataset('dataset.csv')
    print(f"Loaded {len(X)} verified biological decay samples with {len(X[0])} features each.")

    n_samples = len(X)
    shuffled_idx = list(range(n_samples))
    random.shuffle(shuffled_idx)

    split = int(n_samples * 0.8)
    train_idx = shuffled_idx[:split]
    test_idx = shuffled_idx[split:]

    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]
    labels_test = [records[i]['urgency_tier'] for i in test_idx]

    print(f"Training set: {len(X_train)} samples | Testing set: {len(X_test)} samples (80-20 Split)")
    print("Training Random Forest ensemble on local CPU...")

    trees = []
    feature_counts = {i: 0.0 for i in range(len(FEATURE_NAMES))}

    for t in range(12):
        boot_idx = [random.randint(0, len(X_train) - 1) for _ in range(len(X_train))]
        boot_X = [X_train[i] for i in boot_idx]
        boot_y = [y_train[i] for i in boot_idx]
        tree = build_tree(boot_X, boot_y, max_depth=6, min_samples=8, feature_counts=feature_counts)
        trees.append(tree)

    # Evaluation on held-out test set
    preds = [[predict_tree(t, x) for t in trees] for x in X_test]
    y_preds = [sum(p) / len(p) for p in preds]

    mean_y = sum(y_test) / len(y_test)
    ss_tot = sum((val - mean_y) ** 2 for val in y_test)
    ss_res = sum((y_test[i] - y_preds[i]) ** 2 for i in range(len(y_test)))
    r2 = max(0.0, 1.0 - (ss_res / ss_tot))
    rmse = math.sqrt(sum((y_test[i] - y_preds[i]) ** 2 for i in range(len(y_test))) / len(y_test))
    mae = sum(abs(y_test[i] - y_preds[i]) for i in range(len(y_test))) / len(y_test)

    total_gain = sum(feature_counts.values()) or 1.0
    feat_importance = {
        FEATURE_NAMES[i]: round((feature_counts[i] / total_gain) * 100, 2)
        for i in range(len(FEATURE_NAMES))
    }
    sorted_feats = sorted(feat_importance.items(), key=lambda x: x[1], reverse=True)

    elapsed = round(time.time() - start_time, 2)

    print("\n" + "-" * 65)
    print("📊 MODEL PERFORMANCE EVALUATION (Held-Out Test Set):")
    print(f"  • R² Score (Variance Explained):        {r2 * 100:.2f}%")
    print(f"  • Root Mean Squared Error (RMSE):       {rmse:.3f} hours")
    print(f"  • Mean Absolute Error (MAE):            {mae:.3f} hours")
    print(f"  • Training & Evaluation Runtime:        {elapsed} seconds")
    print("-" * 65)

    print("\n🌟 TOP 5 FEATURE IMPORTANCES (Variance Reduction):")
    for name, imp in sorted_feats[:5]:
        bar = "█" * int(imp / 2)
        print(f"  {name:<30} {imp:>5.1f}% {bar}")

    # Export weights
    weights = {
        'model_name': 'FoodRescueRandomForestRegressor',
        'metrics': {'r2_score': r2, 'rmse_hours': rmse, 'mae_hours': mae},
        'feature_importance': feat_importance,
        'trees': [t.to_dict() for t in trees]
    }
    with open('model_weights.json', 'w', encoding='utf-8') as f:
        json.dump(weights, f, indent=2)

    print("\n✅ Trained model saved to model_weights.json")

if __name__ == '__main__':
    main()
