from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your Gupshup API Key (from Sandbox page)
GUPSHUP_API_KEY = "ba069899-a499-4189-98c8-ce00e548a06d"
GUPSHUP_PHONE = "917834811114"   # Your sandbox sender number

@app.route("/")
def home():
    return "Server is running ✅"


@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        # Gupshup might ping this just to check webhook is live
        return "Webhook is live!", 200

    if request.method == "POST":
        data = request.json
        print("Incoming message:", data)

        try:
            msg = data["payload"]["payload"]["text"]  # Gupshup message format
            sender = data["payload"]["source"]        # sender number
        except Exception as e:
            return jsonify({"error": str(e), "data": data}), 400

        # Echo reply
        reply = f"You said: {msg}"
        send_message(sender, reply)

        return jsonify({"status": "ok"}), 200


def send_message(to, message):
    url = "https://api.gupshup.io/wa/api/v1/msg"
    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_PHONE,
        "destination": to,
        "message": f'{{"type":"text","text":"{message}"}}',
        "src.name": "flaskbot"
    }
    headers = {
        "apikey": GUPSHUP_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    print("Reply sent:", response.text)


if __name__ == "__main__":
    app.run(port=5000, debug=True)


from flask import Flask, request, jsonify

app = Flask(__name__)

# Root route - just to test if server is up
@app.route("/")
def home():
    return "✅ Flask server is running with ngrok!"

# Webhook route - for Gupshup
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        data = request.get_json()  # incoming JSON from Gupshup
        print("Received from Gupshup:", data)

        # You can add your logic here (reply, save to DB, etc.)
        return jsonify({"status": "success"}), 200

    # For GET (just for testing in browser)
    return "This is the webhook endpoint for Gupshup ✅"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
