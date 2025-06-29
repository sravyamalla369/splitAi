import streamlit as st
import pandas as pd
import joblib

# Load model
model = joblib.load("model/gradient_boosting_model.pkl")

def predict_split(data: list[dict]) -> dict:
    df = pd.DataFrame(data)
    if "item_sum" in df.columns and "paid_amount" in df.columns:
        total_item_sum = df["item_sum"].sum()
        total_cost_group = df["total_item_cost_group"].iloc[0]
        if abs(total_item_sum - total_cost_group) < 1e-2:
            df["label_balance"] = df["paid_amount"] - df["item_sum"]
            return dict(zip(df["participant_id"], df["label_balance"].round(2)))

    required_cols = [
        'group_size', 'item_count', 'item_sum', 'equal_share',
        'item_share_ratio', 'total_paid_group', 'total_item_cost_group'
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in data: {missing_cols}")

    X = df[required_cols]
    preds = model.predict(X)
    return dict(zip(df['participant_id'], preds.round(2)))

def manual_split(total: float, payer: str, participants: list[str]) -> dict:
    people = participants + [payer]
    per_person = round(total / len(people), 2)
    return {
        person: 0 if person == payer else per_person
        for person in people
    }

# ----------------------- Streamlit UI -----------------------

def main():
    st.title("💸 Smart Split AI")
    st.write("Upload your expense data as a CSV or try manual split.")

    option = st.radio("Choose mode:", ["ML-based Split", "Manual Split"])

    if option == "ML-based Split":
        file = st.file_uploader("Upload CSV with expense data", type=["csv"])
        if file:
            df = pd.read_csv(file)
            st.write("📊 Uploaded Data:", df)
            try:
                result = predict_split(df.to_dict(orient="records"))
                st.success("Predicted balances:")
                st.write(result)
            except Exception as e:
                st.error(f"Prediction failed: {e}")

    else:
        st.subheader("Manual Equal Split")
        total = st.number_input("Total Expense Amount", min_value=0.0)
        payer = st.text_input("Payer Name")
        participants_input = st.text_area("Enter participant names (comma-separated)")
        if st.button("Split"):
            try:
                participants = [p.strip() for p in participants_input.split(",") if p.strip()]
                result = manual_split(total, payer, participants)
                st.success("Split result:")
                st.write(result)
            except Exception as e:
                st.error(f"Manual split failed: {e}")

if __name__ == "__main__":
    main()
