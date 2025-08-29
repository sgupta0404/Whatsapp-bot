import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GUPSHUP_API = "https://api.gupshup.io/wa/api/v1/msg"   # note: /wa/api/v1/msg for WhatsApp
API_KEY = "ogloyetrkp7vsaaamyzecvf69awoiynt"           # sandbox API key
APP_NAME = "whatsappbotdemo"                           # your app name
GUPSHUP_PHONE = "917834811114"                         # sandbox sender number

@app.route("/", methods=["GET"])
def home():
    return "Hello, Render is working! 🚀", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("🔔 Incoming Webhook Data:", data, flush=True)

    try:
        sender = data["payload"]["source"]
        message_text = data["payload"]["payload"].get("text", "")
    except Exception as e:
        print("❌ Error parsing message:", e, flush=True)
        return jsonify({"status": "ignored"}), 200

    print(f"📩 Message from {sender}: {message_text}", flush=True)

    # Rule-based replies
    if "hello" in message_text.lower() or "hi" in message_text.lower():
        reply_text = "👋 Hello! Welcome to our WhatsApp service."
    elif "price" in message_text.lower():
        reply_text = "💰 Our pricing starts at ₹499/month. Would you like details?"
    elif "help" in message_text.lower():
        reply_text = "📞 You can reach support at support@example.com"
    elif "bye" in message_text.lower():
        reply_text = "👋 Goodbye! Have a great day!"
    else:
        reply_text = "🤖 I didn't understand that. Type 'help' for options."

    # Send reply via Gupshup API
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": API_KEY
    }
    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_PHONE,
        "destination": sender,
        "message": f'{{"type":"text","text":"{reply_text}"}}',
        "src.name": APP_NAME
    }

    r = requests.post(GUPSHUP_API, headers=headers, data=payload)
    print("📤 Status Code:", r.status_code, flush=True)
    print("📤 Reply sent:", r.text, flush=True)

    return jsonify({"status": "received"}), 200

