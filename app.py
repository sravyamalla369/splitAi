from flask import Flask, request, jsonify
from smart_split import predict_split, manual_split

app = Flask(__name__)

@app.route("/")
def home():
    return "🧠 Smart + Manual Split API is running!"

@app.route("/api/smart-split", methods=["POST"])
def smart_split_api():
    try:
        req = request.get_json()

        # ✅ Debug print to see what Streamlit is sending
        print("📥 Incoming Request:", req)

        method = req.get("method")

        if method == "manual":
            total = req["total"]
            payer = req["payer"]
            participants = req["participants"]
            result = manual_split(total, payer, participants)
            return jsonify(result)

        elif method == "ml":
            data = req["data"]

            # ✅ Smart logic fallback: if everyone has equal share ratio, use manual
            group_size = data[0]["group_size"]
            equal_ratio = 1 / group_size
            all_equal_share = all(abs(p["item_share_ratio"] - equal_ratio) < 1e-6 for p in data)

            if all_equal_share:
                payer = req.get("payer", "unknown")
                participants = [p["participant_id"] for p in data]
                total = data[0]["total_paid_group"]
                result = manual_split(total, payer, participants)
            else:
                result = predict_split(data)

            return jsonify(result)

        else:
            return jsonify({"error": "Invalid method. Use 'manual' or 'ml'."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
