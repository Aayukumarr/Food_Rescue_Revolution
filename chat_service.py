"""
Food Rescue ML - Intelligent Chatbot & Direct Messaging Service
Provides:
  1. 🤖 AI Food Rescue Assistant (Rule-based & ML Kinetic Knowledge Engine)
  2. 💬 Direct Peer-to-Peer Messaging between Food Donors and NGO Shelters
"""

import json
import os
import time

MESSAGES_FILE = os.path.join(os.path.dirname(__file__), 'messages_data.json')

DEFAULT_MESSAGES = [
    {
        "id": "MSG-101",
        "donation_id": "DON-101",
        "sender_role": "Food Donor Partner",
        "sender_name": "Royal Banquet Hall",
        "sender_phone": "9811223344",
        "message": "Hello, 35 kg mixed veg & pulao is packed in sealed thermal foil containers. Please collect from Gate #2.",
        "timestamp": "Today, 1:45 PM"
    },
    {
        "id": "MSG-102",
        "donation_id": "DON-101",
        "sender_role": "NGO Shelter Coordinator",
        "sender_name": "Robin Hood Army",
        "sender_phone": "9899011223",
        "message": "Received! Volunteer Amit is reaching in an insulated carrier van. ETA 20 minutes.",
        "timestamp": "Today, 1:49 PM"
    },
    {
        "id": "MSG-103",
        "donation_id": "DON-102",
        "sender_role": "Food Donor Partner",
        "sender_name": "Spice Court Restaurant",
        "sender_phone": "9876543210",
        "message": "Paneer curry is fresh and kept at room temperature. Safe window is ~6 hours according to ML scanner.",
        "timestamp": "Today, 2:20 PM"
    },
    {
        "id": "MSG-104",
        "donation_id": "DON-102",
        "sender_role": "NGO Shelter Coordinator",
        "sender_name": "Feeding India Shelter",
        "sender_phone": "9812345678",
        "message": "We have claimed this listing and will distribute it at Central Shelter by 4:00 PM.",
        "timestamp": "Today, 2:25 PM"
    }
]

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    save_messages(DEFAULT_MESSAGES)
    return list(DEFAULT_MESSAGES)

def save_messages(messages):
    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2)
        return True
    except Exception:
        return False

def get_messages_by_donation(donation_id=None):
    all_msgs = load_messages()
    if not donation_id or donation_id == "ALL":
        return all_msgs
    return [m for m in all_msgs if m.get('donation_id') == donation_id]

def send_chat_message(donation_id, sender_role, sender_name, sender_phone, message_text):
    if not message_text.strip():
        return False
    messages = load_messages()
    new_msg = {
        "id": f"MSG-{len(messages) + 101}",
        "donation_id": donation_id or "GENERAL",
        "sender_role": sender_role,
        "sender_name": sender_name or "Anonymous",
        "sender_phone": sender_phone or "9876543210",
        "message": message_text.strip(),
        "timestamp": time.strftime("Today, %I:%M %p")
    }
    messages.append(new_msg)
    save_messages(messages)
    return new_msg

# =========================================================================
# AI FOOD RESCUE ASSISTANT CHATBOT ENGINE
# =========================================================================
BOT_KNOWLEDGE_BASE = [
    {
        "keywords": ["spoil", "safe", "hour", "life", "time", "kitne ghante", "edible"],
        "reply": "🤖 **Spoilage & Shelf-Life AI:**\nCooked meals typically remain safe for **3 to 6 hours** at ambient temperature (28-32°C). Under refrigeration (< 4°C), safe shelf-life extends to **24-48 hours**. Use our real-time ML Spoilage Scanner on the Donor Dashboard for an exact scientific prediction based on humidity and packaging barrier!"
    },
    {
        "keywords": ["temperature", "temp", "garmi", "refrigerat", "cold", "thanda"],
        "reply": "🌡️ **Temperature Impact:**\nAccording to Arrhenius Microbial Kinetics, bacterial growth doubles for every **10°C rise** above 20°C. Keeping food below 4°C halts pathogenic replication and maximizes edible shelf-life."
    },
    {
        "keywords": ["package", "pack", "seal", "foil", "box", "plastic"],
        "reply": "📦 **Packaging Safety Standards:**\n1. **Airtight / Sealed Foil:** Best barrier against airborne spore contamination.\n2. **Cling Film:** Good short-term barrier (extends life by ~1.2 hrs).\n3. **Open Trays:** Highly vulnerable to ambient bacterial inoculation. Avoid open storage."
    },
    {
        "keywords": ["claim", "pickup", "ngo", "volunteer", "collect", "kaise"],
        "reply": "🤝 **NGO Pickup Coordination:**\nWhen an NGO claims a donation on the NGO Shelter Portal, they dispatch an en-route volunteer with insulated carriers. You can use our **Direct Donor-NGO Messenger** to exchange gate numbers and live ETA updates!"
    },
    {
        "keywords": ["dairy", "milk", "paneer", "curd", "doodh"],
        "reply": "🥛 **Dairy Handling Protocol:**\nDairy products have a high moisture and protein content, making them rapid microbial hosts. Dairy should NEVER remain in ambient air > 30°C for more than **3.5 hours**. Always prioritize cold-chain or thermal insulation."
    },
    {
        "keywords": ["carbon", "co2", "environment", "impact", "waste", "benefit"],
        "reply": "🌱 **Environmental Impact Metric:**\nEvery 1 kg of food rescued prevents **2.5 kg of CO₂ equivalent** landfill emissions and saves approximately **1,000 liters of agricultural water**!"
    },
    {
        "keywords": ["urgency", "red alert", "tier", "priority"],
        "reply": "🚨 **ML Urgency Tiers Explained:**\n- **RED ALERT (< 4h safe):** Critical bacterial bloom zone. Immediate pickup required within 2 hours.\n- **HIGH PRIORITY (4-8h safe):** Evening shelter distribution recommended.\n- **NORMAL (> 8h safe):** Safe standard routing schedule."
    }
]

DEFAULT_BOT_REPLY = (
    "🤖 **Food Rescue AI Assistant:**\n"
    "I can assist you with:\n"
    "• Food shelf-life & spoilage predictions\n"
    "• FSSAI surplus food donation guidelines\n"
    "• Temperature & cold-chain preservation tips\n"
    "• Direct NGO pickup coordination\n\n"
    "Try asking: *'How long does cooked food stay safe?'*, *'How do NGOs claim food?'*, or *'How does temperature affect dairy?'*"
)

def get_ai_bot_response(user_query):
    query_lower = user_query.lower()
    for item in BOT_KNOWLEDGE_BASE:
        if any(kw in query_lower for kw in item["keywords"]):
            return item["reply"]
    return DEFAULT_BOT_REPLY
