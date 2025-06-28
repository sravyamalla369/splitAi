# train_model.py

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# ✅ Load the improved dataset
df = pd.read_excel("data/bill_split_dataset_updated_v2.xlsx")

# ✅ Feature Engineering
df["equal_share"] = df["total_item_cost_group"] / df["group_size"]
df["item_share"] = df["item_share_ratio"] * df["total_item_cost_group"]
df["label_balance"] = df["paid_amount"] - df["item_share"]

# ✅ Check for missing values and drop if any
df = df.dropna()

# ✅ Features and Target
X = df[[
    'group_size',
    'item_count',
    'item_sum',
    'equal_share',
    'item_share_ratio',
    'total_paid_group',
    'total_item_cost_group'
]]
y = df["label_balance"]

# ✅ Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ✅ Train the model
model = GradientBoostingRegressor(random_state=42)
model.fit(X_train, y_train)

# ✅ Save the model
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/gradient_boosting_model.pkl")

print("✅ Model trained and saved to model/gradient_boosting_model.pkl")
