# split_ui.py
import streamlit as st
import requests

st.set_page_config(page_title="💸 Smart Bill Splitter", layout="centered")

st.title("💸 Smart Bill Split App")
st.caption("Built with Flask API + Streamlit")

# 👥 Input participant names
names_input = st.text_input("👥 Enter Participants (comma-separated)", placeholder="e.g., rupa, anu, rani")
names = [n.strip().lower() for n in names_input.split(",") if n.strip()]

# Show dynamic paid + item share inputs
paid_amounts = {}
item_shares = {}

if names:
    st.markdown("### 💵 How much did each person pay?")
    for name in names:
        paid_amounts[name] = st.number_input(f"{name.title()} paid (₹)", min_value=0.0, key=f"paid_{name}")

    st.markdown("### 🍴 How much did each person consume?")
    for name in names:
        item_shares[name] = st.number_input(f"{name.title()} consumed worth (₹)", min_value=0.0, key=f"share_{name}")

# 🙋 Payer selector
payer = st.selectbox("🙋 Who Paid?", names) if names else None

# Method selector
method = st.radio("🧠 Choose Split Method", ["Manual", "Smart (ML)"])

if st.button("🔄 Calculate Split"):
    if not names or payer is None:
        st.warning("⚠️ Please enter participants and select a payer.")
    else:
        total_paid = round(sum(paid_amounts.values()), 2)
        total_items = round(sum(item_shares.values()), 2)
        group_size = len(names)
        equal_share = round(total_paid / group_size, 2)

        if method == "Manual":
            friends = [name for name in names if name != payer]
            payload = {
                "method": "manual",
                "total": total_paid,
                "payer": payer,
                "participants": friends
            }
        elif method == "Smart (ML)":
            data = []
            for name in names:
                person_data = {
                    "participant_id": name,
                    "group_size": group_size,
                    "item_count": 1 if item_shares[name] > 0 else 0,
                    "item_sum": item_shares[name],
                    "equal_share": equal_share,
                    "item_share_ratio": item_shares[name] / total_items if total_items > 0 else 1 / group_size,
                    "total_paid_group": total_paid,
                    "total_item_cost_group": total_items if total_items > 0 else total_paid,
                    "paid_amount": paid_amounts[name]
                }
                data.append(person_data)

            payload = {
                "method": "ml",
                "data": data,
                "payer": payer
            }

        # Show API payload
        st.subheader("📤 Payload Sent to API:")
        st.json(payload)

        # Call Flask backend
        try:
            res = requests.post("http://127.0.0.1:5000/api/smart-split", json=payload)
            res.raise_for_status()
            result = res.json()

            st.success("✅ Split Result:")
            for person, amt in result.items():
                st.markdown(f"- **{person}** → ₹{amt}")

            # 📨 Enhanced Message Summary
            st.markdown("---")
            st.markdown("### 📨 Message Summary ")

            receivers = {p: a for p, a in result.items() if a > 0}
            payers = {p: -a for p, a in result.items() if a < 0}

            messages = []
            for payer_name, owe_amt in payers.items():
                remaining = owe_amt
                for receiver_name in receivers:
                    if receivers[receiver_name] == 0:
                        continue
                    pay_amt = min(remaining, receivers[receiver_name])
                    if pay_amt > 0:
                        messages.append(
                            f"📤 **{payer_name.title()} should pay ₹{pay_amt:.2f} to {receiver_name.title()}**"
                        )
                        receivers[receiver_name] -= pay_amt
                        remaining -= pay_amt
                    if remaining <= 0:
                        break

            if messages:
                for msg in messages:
                    st.markdown(msg)
            else:
                st.info("All participants are already settled.")

        except Exception as e:
            st.error(f"❌ API Error: {e}")