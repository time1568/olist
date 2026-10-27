import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import roc_auc_score, average_precision_score

print("Loading feature dataset...")
df = pd.read_csv("data/training_features.csv")

# 1. Sort chronologically for temporal validation
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df = df.sort_values("order_purchase_timestamp").reset_index(drop=True)

# 2. 3-Way Temporal Split (70% Train, 15% Val, 15% Test)
n_total = len(df)
train_end = int(n_total * 0.70)
val_end = int(n_total * 0.85)

train_df = df.iloc[:train_end]
val_df = df.iloc[train_end:val_end]
test_df = df.iloc[val_end:]

print(f"Chronological Splits:")
print(f" - Train: {train_df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} to {train_df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')} ({len(train_df):,} rows, {train_df['is_late'].mean():.2%} late)")
print(f" - Val:   {val_df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} to {val_df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')} ({len(val_df):,} rows, {val_df['is_late'].mean():.2%} late)")
print(f" - Test:  {test_df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} to {test_df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')} ({len(test_df):,} rows, {test_df['is_late'].mean():.2%} late)")

# 3. Separate features and target
drop_cols = ["order_id", "order_purchase_timestamp", "is_late"]

X_train = train_df.drop(columns=drop_cols)
y_train = train_df["is_late"]

X_val = val_df.drop(columns=drop_cols)
y_val = val_df["is_late"]

X_test = test_df.drop(columns=drop_cols)
y_test = test_df["is_late"]

# 4. Categoricals
cat_cols = ["customer_state", "seller_state"]
for col in cat_cols:
    X_train[col] = X_train[col].astype("category")
    X_val[col] = X_val[col].astype("category")
    X_test[col] = X_test[col].astype("category")

neg_count = (y_train == 0).sum()
pos_count = (y_train == 1).sum()
scale_weight = neg_count / pos_count

# 5. Tree Hyperparameter Tuning on VALIDATION set ONLY
candidate_trees = [50, 100, 150, 200, 250, 300]
val_scores = {}

print("\n--- Tuning Ensemble Size on Validation Holdout ---")
for n_trees in candidate_trees:
    clf = lgb.LGBMClassifier(
        n_estimators=n_trees,
        learning_rate=0.03,
        num_leaves=31,
        min_child_samples=50,
        scale_pos_weight=scale_weight,
        objective="binary",
        random_state=42,
        importance_type="gain",
        verbose=-1
    )
    clf.fit(X_train, y_train)
    val_probs = clf.predict_proba(X_val)[:, 1]
    val_auc = roc_auc_score(y_val, val_probs)
    val_scores[n_trees] = val_auc
    print(f"  Trees: {n_trees:3d} | Validation ROC-AUC: {val_auc:.4f}")

best_trees = max(val_scores, key=val_scores.get)
print(f"\n--> Selected {best_trees} trees based on peak Validation ROC-AUC ({val_scores[best_trees]:.4f})")

# 6. Fit Final Model with Chosen Tree Size
final_model = lgb.LGBMClassifier(
    n_estimators=best_trees,
    learning_rate=0.03,
    num_leaves=31,
    min_child_samples=50,
    scale_pos_weight=scale_weight,
    objective="binary",
    random_state=42,
    importance_type="gain",
    verbose=-1
)
final_model.fit(X_train, y_train)

# 7. Unbiased Evaluation on Untouched TEST set
y_test_probs = final_model.predict_proba(X_test)[:, 1]

roc_auc = roc_auc_score(y_test, y_test_probs)
pr_auc = average_precision_score(y_test, y_test_probs)

print(f"\n=== FINAL TEST METRICS (Selected Trees: {best_trees}) ===")
print(f"ROC-AUC Score:      {roc_auc:.4f}")
print(f"PR-AUC (Avg Prec):  {pr_auc:.4f} (Baseline test late rate: {y_test.mean():.4f})")

# 8. Decile Capture Metrics
test_results = pd.DataFrame({
    "actual": y_test.values,
    "prob": y_test_probs
}).sort_values(by="prob", ascending=False)

top_10_pct_cutoff = int(len(test_results) * 0.10)
top_10_pct = test_results.iloc[:top_10_pct_cutoff]
captured_late_orders = top_10_pct['actual'].sum()
total_late_orders = test_results['actual'].sum()
capture_rate = captured_late_orders / total_late_orders

print(f"\n=== BUSINESS VALUE METRICS (TEMPORAL HOLDOUT) ===")
print(f"Top 10% Highest-Risk Flagged Orders: {top_10_pct_cutoff:,}")
print(f"Actual Late Orders in Top 10%:       {captured_late_orders:,} out of {total_late_orders:,}")
print(f"Top Decile Capture Rate:             {capture_rate:.2%}")
print(f"Delay Rate inside Top 10% Flagged:   {top_10_pct['actual'].mean():.2%}")