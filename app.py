# # use these 2 lines when you want to load values from .env file locally

# # from dotenv import load_dotenv
# # load_dotenv()

# import os
# import google.generativeai as genai
# import requests
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# # Gupshup configs
# GUPSHUP_API = "https://api.gupshup.io/wa/api/v1/msg"  # WhatsApp endpoint
# API_KEY = os.getenv("GUPSHUP_API_KEY")
# APP_NAME = os.getenv("GUPSHUP_APP_NAME")
# GUPSHUP_PHONE = os.getenv("GUPSHUP_PHONE")

# # Gemini configs
# GENAI_API_KEY = os.getenv("GENAI_API_KEY")
# genai.configure(api_key=GENAI_API_KEY)

# def get_ai_reply(user_message: str) -> str:
#     """Get smart AI reply using Gemini Pro"""
#     try:
#         model = genai.GenerativeModel("gemini-2.5-flash-lite")
#         response = model.generate_content(user_message)
#         return response.text.strip()
#     except Exception as e:
#         print("❌ Gemini error:", e, flush=True)
#         return "⚠️ Sorry, I couldn't process that right now."

# @app.route("/", methods=["GET"])
# def home():
#     return "Hello, Render + Gemini is working! 🚀", 200

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     data = request.get_json(force=True)
#     print("🔔 Incoming Webhook Data:", data, flush=True)

#     try:
#         sender = data["payload"]["source"]
#         message_text = data["payload"]["payload"].get("text", "")
#     except Exception as e:
#         print("❌ Error parsing message:", e, flush=True)
#         return jsonify({"status": "ignored"}), 200

#     print(f"📩 Message from {sender}: {message_text}", flush=True)

#     # 🔹 Gemini reply
#     reply_text = get_ai_reply(message_text)

#     # Send reply via Gupshup API
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "apikey": API_KEY
#     }
#     payload = {
#         "channel": "whatsapp",
#         "source": GUPSHUP_PHONE,
#         "destination": sender,
#         "message": f'{{"type":"text","text":"{reply_text}"}}',
#         "src.name": APP_NAME
#     }

#     r = requests.post(GUPSHUP_API, headers=headers, data=payload)
#     print("📤 Status Code:", r.status_code, flush=True)
#     print("📤 Reply sent:", r.text, flush=True)

#     return jsonify({"status": "received"}), 200

import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 🔹 Config
GUPSHUP_API = "https://api.gupshup.io/wa/api/v1/msg"
API_KEY = os.getenv("GUPSHUP_API_KEY")
APP_NAME = os.getenv("GUPSHUP_APP_NAME")
GUPSHUP_PHONE = os.getenv("GUPSHUP_PHONE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

    # 🔹 Add to conversation history
    if sender not in conversations:
        conversations[sender] = []
    conversations[sender].append({"role": "user", "text": message_text})

    # 🔹 Keep only last 5 messages for memory
    if len(conversations[sender]) > 5:
        conversations[sender] = conversations[sender][-5:]

    # 🔹 Prepare context for Gemini
    history = "\n".join([f"{msg['role']}: {msg['text']}" for msg in conversations[sender]])

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(f"Here is the chat history:\n{history}\n\nReply as a helpful assistant:")
        reply_text = response.text
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
        "message": f'{{"type":"text","text":"{reply_text}"}}',
        "src.name": APP_NAME
    }

    r = requests.post(GUPSHUP_API, headers=headers, data=payload)
    print("📤 Status Code:", r.status_code, flush=True)
    print("📤 Reply sent:", r.text, flush=True)

    return jsonify({"status": "received"}), 200
