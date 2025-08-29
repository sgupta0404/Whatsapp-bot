# from flask import Flask, request, jsonify
# import requests

# app = Flask(__name__)

# # Replace with your Gupshup API Key (from Sandbox page)
# GUPSHUP_API_KEY = "ogloyetrkp7vsaaamyzecvf69awoiynt"
# GUPSHUP_PHONE = "917834811114"   # Your sandbox sender number

# @app.route("/")
# def home():
#     return "Server is running ✅"


# @app.route("/webhook", methods=["POST", "GET"])
# def webhook():
#     if request.method == "GET":
#         # Gupshup might ping this just to check webhook is live
#         return "Webhook is live!", 200

#     if request.method == "POST":
#         data = request.json
#         print("Incoming message:", data)

#         try:
#             msg = data["payload"]["payload"]["text"]  # Gupshup message format
#             sender = data["payload"]["source"]        # sender number
#         except Exception as e:
#             return jsonify({"error": str(e), "data": data}), 400

#         # Echo reply
#         reply = f"You said: {msg}"
#         send_message(sender, reply)

#         return jsonify({"status": "ok"}), 200


# def send_message(to, message):
#     url = "https://api.gupshup.io/wa/api/v1/msg"
#     payload = {
#         "channel": "whatsapp",
#         "source": GUPSHUP_PHONE,
#         "destination": to,
#         "message": f'{{"type":"text","text":"{message}"}}',
#         "src.name": "flaskbot"
#     }
#     headers = {
#         "apikey": GUPSHUP_API_KEY,
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     response = requests.post(url, data=payload, headers=headers)
#     print("Reply sent:", response.text)


# if __name__ == "__main__":
#     app.run(port=5000, debug=True)


# from flask import Flask, request, jsonify

# app = Flask(__name__)

# # Root route - just to test if server is up
# @app.route("/")
# def home():
#     return "✅ Flask server is running with ngrok!"

# # Webhook route - for Gupshup
# @app.route("/webhook", methods=["POST", "GET"])
# def webhook():
#     if request.method == "POST":
#         data = request.get_json()  # incoming JSON from Gupshup
#         print("Received from Gupshup:", data)

#         # You can add your logic here (reply, save to DB, etc.)
#         return jsonify({"status": "success"}), 200

#     # For GET (just for testing in browser)
#     return "This is the webhook endpoint for Gupshup ✅"

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)


# from flask import Flask, request, jsonify

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "WhatsApp Bot is running!", 200

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     data = request.json
#     print("Incoming message:", data)

#     # extract message (Meta format v3 from Gupshup)
#     try:
#         sender = data["messages"][0]["from"]
#         message = data["messages"][0]["text"]["body"]
#     except Exception as e:
#         print("Error extracting message:", e)
#         return jsonify({"status": "ignored"})

#     # simple reply logic
#     if "hi" in message.lower():
#         reply = "Hello 👋! How can I help you today?"
#     else:
#         reply = f"You said: {message}"

#     # IMPORTANT: returning JSON doesn’t send reply to WhatsApp directly
#     # Instead, you must call Gupshup API to reply (we’ll add this later)
#     return jsonify({"reply": reply})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)


# from flask import Flask, request, jsonify

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return "Hello, Render is working! 🚀", 200

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     try:
#         data = request.get_json(force=True)
#     except Exception:
#         data = {"error": "Could not parse JSON", "raw": request.data.decode("utf-8")}
    
#     print("🔔 Incoming Webhook Data:", data, flush=True)  # always print
    
#     return jsonify({"status": "received"}), 200


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

