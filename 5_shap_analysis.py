import pandas as pd
import numpy as np
import lightgbm as lgb
import shap
import matplotlib.pyplot as plt

print("Loading feature dataset...")
df = pd.read_csv("data/training_features.csv")
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df = df.sort_values("order_purchase_timestamp").reset_index(drop=True)

# 1. 3-Way Temporal Split
n_total = len(df)
train_end = int(n_total * 0.70)
val_end = int(n_total * 0.85)

train_df = df.iloc[:train_end]
val_df = df.iloc[train_end:val_end]
test_df = df.iloc[val_end:]

drop_cols = ["order_id", "order_purchase_timestamp", "is_late"]

X_train = train_df.drop(columns=drop_cols)
y_train = train_df["is_late"]

X_val = val_df.drop(columns=drop_cols)
y_val = val_df["is_late"]

X_test = test_df.drop(columns=drop_cols)
y_test = test_df["is_late"]

# Encode categorical columns
cat_cols = ["customer_state", "seller_state"]
for col in cat_cols:
    X_train[col] = X_train[col].astype("category")
    X_val[col] = X_val[col].astype("category")
    X_test[col] = X_test[col].astype("category")

neg_count = (y_train == 0).sum()
pos_count = (y_train == 1).sum()
scale_weight = neg_count / pos_count

# 2. Train fixed 100-tree model
model = lgb.LGBMClassifier(
    n_estimators=300,
    learning_rate=0.03,
    num_leaves=31,
    min_child_samples=50,
    scale_pos_weight=scale_weight,
    objective="binary",
    random_state=42,
    importance_type="gain",
    verbose=-1
)

print("Training model across chronological history (300 trees)...")
# try:
#     model.fit(X_train, y_train, eval_X=X_val, eval_y=y_val)
# except (TypeError, ValueError):
#     model.fit(X_train, y_train)
model.fit(X_train, y_train)

print(f"Model trained successfully with {model.n_estimators} trees.")

# 3. Compute SHAP Values on Out-of-Time Test Sample
print("Computing SHAP values on out-of-time test holdout...")
sample_X_test = X_test.sample(2000, random_state=42)

explainer = shap.TreeExplainer(model)
shap_explanation = explainer(sample_X_test)

if len(shap_explanation.values.shape) == 3:
    shap_vals_late = shap_explanation.values[:, :, 1]
elif isinstance(shap_explanation.values, list):
    shap_vals_late = shap_explanation.values[1]
else:
    shap_vals_late = shap_explanation.values

# 4. Generate and Save Summary Plot
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_vals_late, sample_X_test, show=False)
plt.title("Top Delay Drivers (Temporal Holdout SHAP)", fontsize=14, pad=15)
plt.tight_layout()
plt.savefig("deliverables/shap_summary_plot.png", dpi=300)
print("Saved updated plot to 'deliverables/shap_summary_plot.png'")

# 5. Extract Feature Impact Rankings
mean_abs_shap = np.abs(shap_vals_late).mean(axis=0)
shap_rankings = pd.DataFrame({
    "Feature": sample_X_test.columns,
    "Mean_Absolute_SHAP": mean_abs_shap
}).sort_values(by="Mean_Absolute_SHAP", ascending=False)

print("\n=== RANKED DELAY DRIVERS (OUT-OF-TIME) ===")
print(shap_rankings.to_string(index=False))