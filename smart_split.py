import pandas as pd
import joblib

# Load the trained ML model once
model = joblib.load("model/gradient_boosting_model.pkl")

def predict_split(data: list[dict]) -> dict:
    """
    Predict how much each participant owes or should be reimbursed.
    Fallback: If item_sum and paid_amount are available & match total_item_cost_group,
    use rule-based logic: label_balance = paid_amount - item_sum
    """
    df = pd.DataFrame(data)

    # Check if item_sum and paid_amount columns are provided
    if "item_sum" in df.columns and "paid_amount" in df.columns:
        total_item_sum = df["item_sum"].sum()
        total_cost_group = df["total_item_cost_group"].iloc[0]

        # ✅ Use rule-based logic if item sums match total
        if abs(total_item_sum - total_cost_group) < 1e-2:
            df["label_balance"] = df["paid_amount"] - df["item_sum"]
            return dict(zip(df["participant_id"], df["label_balance"].round(2)))

    # ✅ Otherwise, use ML model
    required_cols = [
        'group_size',
        'item_count',
        'item_sum',
        'equal_share',
        'item_share_ratio',
        'total_paid_group',
        'total_item_cost_group'
    ]

    # Check for missing columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in data: {missing_cols}")

    X = df[required_cols]
    preds = model.predict(X)
    return dict(zip(df['participant_id'], preds.round(2)))

def manual_split(total: float, payer: str, participants: list[str]) -> dict:
    """
    Equal split among all participants, with payer exempt.
    """
    people = participants + [payer]
    per_person = round(total / len(people), 2)

    return {
        person: 0 if person == payer else per_person
        for person in people
    } 
