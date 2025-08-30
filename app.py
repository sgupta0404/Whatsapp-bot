# use these 2 lines when you want to load values from .env file locally

# from dotenv import load_dotenv
# load_dotenv()

import os
import google.generativeai as genai
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Gupshup configs
GUPSHUP_API = "https://api.gupshup.io/wa/api/v1/msg"  # WhatsApp endpoint
API_KEY = os.getenv("GUPSHUP_API_KEY")
APP_NAME = os.getenv("GUPSHUP_APP_NAME")
GUPSHUP_PHONE = os.getenv("GUPSHUP_PHONE")

# Gemini configs
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

def get_ai_reply(user_message: str) -> str:
    """Get smart AI reply using Gemini Pro"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash:generateContent")
        response = model.generate_content(user_message)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini error:", e, flush=True)
        return "⚠️ Sorry, I couldn't process that right now."

@app.route("/", methods=["GET"])
def home():
    return "Hello, Render + Gemini is working! 🚀", 200

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

    # 🔹 Gemini reply
    reply_text = get_ai_reply(message_text)

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