"""
Food Rescue Revolution - Machine Learning Model Trainer
Trains an Ensemble Random Forest Regressor & Multi-Class Classifier for food spoilage shelf-life prediction.
Written using Python Standard Library for 100% dependency-free execution and evaluation.
"""

import csv
import json
import math
import random
import time

random.seed(42)

FEATURE_NAMES = [
    'category_cooked_meals',
    'category_dairy',
    'category_bakery',
    'category_fresh_produce',
    'category_packaged_goods',
    'food_type_veg',
    'food_type_non_veg',
    'food_type_vegan',
    'ambient_temp_c',
    'humidity_percent',
    'storage_ambient_room',
    'storage_refrigerated',
    'storage_thermal_insulated',
    'packaging_open_container',
    'packaging_plastic_wrap',
    'packaging_sealed_foil',
    'packaging_airtight_vacuum',
    'prepared_hours_ago'
]

def encode_row(row):
    cat = row['category']
    ft = row['food_type']
    st = row['storage_condition']
    pk = row['packaging_type']

    return [
        1.0 if cat == 'cooked_meals' else 0.0,
        1.0 if cat == 'dairy' else 0.0,
        1.0 if cat == 'bakery' else 0.0,
        1.0 if cat == 'fresh_produce' else 0.0,
        1.0 if cat == 'packaged_goods' else 0.0,
        1.0 if ft == 'veg' else 0.0,
        1.0 if ft == 'non_veg' else 0.0,
        1.0 if ft == 'vegan' else 0.0,
        float(row['ambient_temp_c']),
        float(row['humidity_percent']),
        1.0 if st == 'ambient_room' else 0.0,
        1.0 if st == 'refrigerated' else 0.0,
        1.0 if st == 'thermal_insulated' else 0.0,
        1.0 if pk == 'open_container' else 0.0,
        1.0 if pk == 'plastic_wrap' else 0.0,
        1.0 if pk == 'sealed_foil' else 0.0,
        1.0 if pk == 'airtight_vacuum' else 0.0,
        float(row['prepared_hours_ago'])
    ]

def load_data(filepath='ml/dataset.csv'):
    X, y, labels = [], [], []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            X.append(encode_row(row))
            y.append(float(row['remaining_shelf_life_hours']))
            labels.append(row['urgency_tier'])
    return X, y, labels

# Decision Tree Regressor Implementation
class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    def to_dict(self):
        if self.value is not None:
            return {'val': round(self.value, 3)}
        return {
            'feat': self.feature,
            'th': round(self.threshold, 3),
            'l': self.left.to_dict(),
            'r': self.right.to_dict()
        }

def variance(y_vals):
    if len(y_vals) <= 1:
        return 0.0
    mean = sum(y_vals) / len(y_vals)
    return sum((v - mean) ** 2 for v in y_vals) / len(y_vals)

def build_tree(X, y, depth=0, max_depth=6, min_samples=8, max_features=8, feature_counts=None):
    if len(y) <= min_samples or depth >= max_depth:
        return DecisionTreeNode(value=sum(y) / len(y))

    current_var = variance(y)
    if current_var < 0.01:
        return DecisionTreeNode(value=sum(y) / len(y))

    n_features = len(X[0])
    feature_indices = random.sample(range(n_features), min(max_features, n_features))

    best_gain = -1
    best_feat = None
    best_thresh = None
    best_splits = None

    for f_idx in feature_indices:
        vals = [row[f_idx] for row in X]
        unique_vals = sorted(set(vals))
        if len(unique_vals) <= 1:
            continue

        # Subsample thresholds if many
        if len(unique_vals) > 12:
            thresholds = [unique_vals[int(len(unique_vals) * p)] for p in [0.15, 0.3, 0.45, 0.6, 0.75, 0.9]]
        else:
            thresholds = [(unique_vals[i] + unique_vals[i+1]) / 2.0 for i in range(len(unique_vals)-1)]

        for th in thresholds:
            left_y = [y[i] for i in range(len(X)) if X[i][f_idx] <= th]
            right_y = [y[i] for i in range(len(X)) if X[i][f_idx] > th]

            if len(left_y) < 3 or len(right_y) < 3:
                continue

            var_left = variance(left_y)
            var_right = variance(right_y)
            gain = current_var - ((len(left_y)/len(y)) * var_left + (len(right_y)/len(y)) * var_right)

            if gain > best_gain:
                best_gain = gain
                best_feat = f_idx
                best_thresh = th
                best_splits = (
                    [X[i] for i in range(len(X)) if X[i][f_idx] <= th],
                    left_y,
                    [X[i] for i in range(len(X)) if X[i][f_idx] > th],
                    right_y
                )

    if best_gain <= 0.001 or best_splits is None:
        return DecisionTreeNode(value=sum(y) / len(y))

    if feature_counts is not None and best_feat is not None:
        feature_counts[best_feat] += best_gain * len(y)

    left_X, left_y, right_X, right_y = best_splits
    left_node = build_tree(left_X, left_y, depth + 1, max_depth, min_samples, max_features, feature_counts)
    right_node = build_tree(right_X, right_y, depth + 1, max_depth, min_samples, max_features, feature_counts)
    return DecisionTreeNode(feature=best_feat, threshold=best_thresh, left=left_node, right=right_node)

def predict_single_tree(node, x):
    if node.value is not None:
        return node.value
    if x[node.feature] <= node.threshold:
        return predict_single_tree(node.left, x)
    return predict_single_tree(node.right, x)

def train_random_forest(X_train, y_train, n_trees=12, max_depth=6, min_samples=8):
    trees = []
    feature_counts = {i: 0.0 for i in range(len(X_train[0]))}

    for t in range(n_trees):
        # Bootstrap sample with replacement
        indices = [random.randint(0, len(X_train) - 1) for _ in range(len(X_train))]
        boot_X = [X_train[i] for i in indices]
        boot_y = [y_train[i] for i in indices]

        tree = build_tree(boot_X, boot_y, max_depth=max_depth, min_samples=min_samples, feature_counts=feature_counts)
        trees.append(tree)

    return trees, feature_counts

def predict_forest(trees, x):
    preds = [predict_single_tree(tree, x) for tree in trees]
    return sum(preds) / len(preds)

def main():
    print("=" * 60)
    print("🤖 FOOD RESCUE REVOLUTION - MACHINE LEARNING PIPELINE")
    print("Algorithm: Ensemble Random Forest Regressor & Urgency Classifier")
    print("=" * 60)

    start_time = time.time()
    X, y, labels = load_data('ml/dataset.csv')
    print(f"Loaded {len(X)} samples with {len(X[0])} features each.")

    # 80/20 Train-Test Split
    n_samples = len(X)
    shuffled_idx = list(range(n_samples))
    random.shuffle(shuffled_idx)

    split_point = int(n_samples * 0.8)
    train_idx = shuffled_idx[:split_point]
    test_idx = shuffled_idx[split_point:]

    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]
    labels_test = [labels[i] for i in test_idx]

    print(f"Training dataset size: {len(X_train)} | Test dataset size: {len(X_test)}")
    print("Training Random Forest ensemble (12 trees, max_depth=6)...")

    trees, feat_importance_raw = train_random_forest(X_train, y_train, n_trees=12, max_depth=6, min_samples=8)

    # Evaluate on held-out Test Set
    y_preds = [predict_forest(trees, x) for x in X_test]

    # Metrics calculation
    mae = sum(abs(y_test[i] - y_preds[i]) for i in range(len(y_test))) / len(y_test)
    mse = sum((y_test[i] - y_preds[i]) ** 2 for i in range(len(y_test))) / len(y_test)
    rmse = math.sqrt(mse)

    mean_y_test = sum(y_test) / len(y_test)
    ss_total = sum((v - mean_y_test) ** 2 for v in y_test)
    ss_res = sum((y_test[i] - y_preds[i]) ** 2 for i in range(len(y_test)))
    r2_score = 1.0 - (ss_res / ss_total)

    # Classification matrix on urgency tier
    tier_classes = ['NORMAL', 'HIGH_PRIORITY', 'RED_ALERT', 'CRITICAL_EXPIRED']
    def get_tier(hrs):
        if hrs <= 0.2:
            return 'CRITICAL_EXPIRED'
        if hrs <= 2.5:
            return 'RED_ALERT'
        if hrs <= 6.0:
            return 'HIGH_PRIORITY'
        return 'NORMAL'

    pred_tiers = [get_tier(p) for p in y_preds]
    correct_tiers = sum(1 for i in range(len(y_test)) if pred_tiers[i] == labels_test[i])
    classification_acc = (correct_tiers / len(y_test)) * 100.0

    # Normalized feature importance
    total_imp = sum(feat_importance_raw.values()) or 1.0
    feat_importance = {
        FEATURE_NAMES[idx]: round((feat_importance_raw[idx] / total_imp) * 100, 2)
        for idx in range(len(FEATURE_NAMES))
    }
    sorted_features = sorted(feat_importance.items(), key=lambda x: x[1], reverse=True)

    elapsed = round(time.time() - start_time, 2)

    print("\n" + "-" * 60)
    print("📊 MODEL EVALUATION METRICS (Held-Out Test Set):")
    print(f"  • R² Score (Coefficient of Determination): {r2_score * 100:.2f}%")
    print(f"  • Root Mean Squared Error (RMSE):        {rmse:.3f} hours")
    print(f"  • Mean Absolute Error (MAE):             {mae:.3f} hours")
    print(f"  • Urgency Classification Accuracy:       {classification_acc:.2f}%")
    print(f"  • Training & Evaluation Runtime:         {elapsed}s")
    print("-" * 60)

    print("\n🌟 TOP 5 FEATURE IMPORTANCES:")
    for name, imp in sorted_features[:5]:
        bar = "█" * int(imp / 2)
        print(f"  {name:<30} {imp:>5.1f}% {bar}")

    # Export Model Weights & Meta
    model_export = {
        'model_name': 'FoodSpoliageRandomForestRegressor',
        'algorithm': 'Random Forest Ensemble Regressor + Tier Classifier',
        'version': '1.0.0',
        'trained_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'metrics': {
            'r2_score': round(r2_score, 4),
            'r2_percentage': round(r2_score * 100, 2),
            'rmse_hours': round(rmse, 3),
            'mae_hours': round(mae, 3),
            'classification_accuracy': round(classification_acc, 2),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'total_samples': len(X)
        },
        'feature_names': FEATURE_NAMES,
        'feature_importance': feat_importance,
        'top_features': sorted_features,
        'hyperparameters': {
            'n_estimators': len(trees),
            'max_depth': 6,
            'min_samples_split': 8,
            'criterion': 'variance_reduction_mse'
        },
        'trees': [t.to_dict() for t in trees]
    }

    with open('ml/model_weights.json', 'w', encoding='utf-8') as f:
        json.dump(model_export, f, indent=2)

    print(f"\n✅ Model serialized to ml/model_weights.json (Ready for zero-latency inference).")

if __name__ == '__main__':
    main()
