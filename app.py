import os
import json
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 🔹 Config (from Render Environment Variables)
GUPSHUP_API = "https://api.gupshup.io/wa/api/v1/msg"
API_KEY = os.getenv("GUPSHUP_API_KEY")
APP_NAME = os.getenv("GUPSHUP_APP_NAME")
GUPSHUP_PHONE = os.getenv("GUPSHUP_PHONE")
GEMINI_API_KEY = os.getenv("GENAI_API_KEY")

# 🔹 Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Simple memory storage (dict: sender -> conversation history)
conversations = {}

@app.route("/", methods=["GET"])
def home():
    return "🚀 WhatsApp Bot with Memory is running!"

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

    # 🔹 Check special commands
    if message_text.lower() == "/reset":
        conversations[sender] = []  # clear history
        reply_text = "🧹 Memory cleared! Let's start fresh."
    elif message_text.lower() == "/help":
        reply_text = (
            "📖 *Available Commands:*\n"
            "- `/help` → Show this help message\n"
            "- `/reset` → Clear chat memory\n\n"
            "💡 Just type normally to chat with me!"
        )
    else:
        # 🔹 Add to conversation history
        if sender not in conversations:
            conversations[sender] = []
        conversations[sender].append({"role": "user", "text": message_text})

        # 🔹 Keep only last 5 messages
        if len(conversations[sender]) > 5:
            conversations[sender] = conversations[sender][-5:]

        # 🔹 Prepare context for Gemini
        history = "\n".join([f"{msg['role']}: {msg['text']}" for msg in conversations[sender]])

        try:
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            response = model.generate_content(
                f"Here is the chat history:\n{history}\n\nReply as a helpful assistant:"
            )
            reply_text = response.text.strip()  # remove unwanted \n
        except Exception as e:
            reply_text = "⚠️ Sorry, I'm having trouble replying right now."
            print("❌ Gemini Error:", e, flush=True)

        # 🔹 Add bot reply to memory
        conversations[sender].append({"role": "bot", "text": reply_text})

    # 🔹 Send reply via Gupshup API
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": API_KEY
    }
    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_PHONE,
        "destination": sender,
        "message": json.dumps({"type": "text", "text": reply_text}),
        "src.name": APP_NAME
    }

    r = requests.post(GUPSHUP_API, headers=headers, data=payload)
    print("📤 Status Code:", r.status_code, flush=True)
    print("📤 Reply sent:", r.text, flush=True)

    return jsonify({"status": "received"}), 200
