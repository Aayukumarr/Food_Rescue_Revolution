"""
Food Rescue ML - Shared Donations Store
Manages food listings between Donor Dashboard and NGO Dashboard.
Supports adding donations with ML Spoilage predictions and claiming by NGOs.
"""

import json
import os
import time

DATA_FILE = os.path.join(os.path.dirname(__file__), 'donations_data.json')

DEFAULT_DONATIONS = [
    {
        "id": "DON-101",
        "food_name": "Wedding Buffet Mixed Veg & Pulao",
        "category": "cooked_meals",
        "food_type": "veg",
        "quantity_kg": 35.0,
        "servings": 100,
        "donor_name": "Royal Banquet Hall",
        "donor_phone": "9811223344",
        "donor_location": "South Delhi, Sector 4",
        "ambient_temp_c": 31.5,
        "storage_condition": "ambient_room",
        "prepared_hours_ago": 2.5,
        "predicted_safe_hours": 3.8,
        "urgency_tier": "RED_ALERT",
        "status": "AVAILABLE",
        "claimed_by": None,
        "claimed_phone": None,
        "timestamp": "Today, 1:30 PM"
    },
    {
        "id": "DON-102",
        "food_name": "Surplus Paneer Curry & Fresh Naan",
        "category": "cooked_meals",
        "food_type": "veg",
        "quantity_kg": 20.0,
        "servings": 60,
        "donor_name": "Spice Court Restaurant",
        "donor_phone": "9876543210",
        "donor_location": "Connaught Place, Central Delhi",
        "ambient_temp_c": 28.0,
        "storage_condition": "thermal_insulated",
        "prepared_hours_ago": 1.5,
        "predicted_safe_hours": 6.2,
        "urgency_tier": "HIGH_PRIORITY",
        "status": "AVAILABLE",
        "claimed_by": None,
        "claimed_phone": None,
        "timestamp": "Today, 2:15 PM"
    },
    {
        "id": "DON-103",
        "food_name": "Fresh Apples, Bananas & Seasonal Melons",
        "category": "fresh_produce",
        "food_type": "vegan",
        "quantity_kg": 50.0,
        "servings": 150,
        "donor_name": "Green Mandi Wholesalers",
        "donor_phone": "9899887766",
        "donor_location": "Azadpur Mandi, Delhi",
        "ambient_temp_c": 26.0,
        "storage_condition": "ambient_room",
        "prepared_hours_ago": 0.5,
        "predicted_safe_hours": 72.0,
        "urgency_tier": "NORMAL",
        "status": "AVAILABLE",
        "claimed_by": None,
        "claimed_phone": None,
        "timestamp": "Today, 11:00 AM"
    },
    {
        "id": "DON-104",
        "food_name": "Pasteurized Milk Packets & Curd Cups",
        "category": "dairy",
        "food_type": "veg",
        "quantity_kg": 15.0,
        "servings": 45,
        "donor_name": "City Cafe & Bakery",
        "donor_phone": "9711002233",
        "donor_location": "Noida, Sector 18",
        "ambient_temp_c": 24.0,
        "storage_condition": "refrigerated",
        "prepared_hours_ago": 3.0,
        "predicted_safe_hours": 18.5,
        "urgency_tier": "NORMAL",
        "status": "CLAIMED",
        "claimed_by": "Robin Hood Army (Noida Chapter)",
        "claimed_phone": "9899011223",
        "timestamp": "Today, 10:30 AM"
    }
]

def load_donations():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    save_donations(DEFAULT_DONATIONS)
    return list(DEFAULT_DONATIONS)

def save_donations(donations):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(donations, f, indent=2)
        return True
    except Exception:
        return False

def add_new_donation(data):
    donations = load_donations()
    new_id = f"DON-{len(donations) + 101}"
    data['id'] = new_id
    data['status'] = 'AVAILABLE'
    data['claimed_by'] = None
    data['claimed_phone'] = None
    data['timestamp'] = time.strftime("Today, %I:%M %p")
    donations.insert(0, data)
    save_donations(donations)
    return new_id

def claim_donation_by_ngo(donation_id, ngo_name, ngo_phone):
    donations = load_donations()
    found = False
    for d in donations:
        if d['id'] == donation_id:
            d['status'] = 'CLAIMED'
            d['claimed_by'] = ngo_name
            d['claimed_phone'] = ngo_phone
            found = True
            break
    if found:
        save_donations(donations)
    return found

def get_stats():
    donations = load_donations()
    total_kg = sum(d.get('quantity_kg', 0) for d in donations)
    total_servings = sum(d.get('servings', 0) for d in donations)
    claimed_donations = [d for d in donations if d.get('status') == 'CLAIMED']
    available_donations = [d for d in donations if d.get('status') == 'AVAILABLE']
    urgent_available = [d for d in available_donations if d.get('urgency_tier') in ['RED_ALERT', 'HIGH_PRIORITY']]
    co2_saved_kg = round(sum(d.get('quantity_kg', 0) for d in claimed_donations) * 2.5, 1)

    return {
        'total_listings': len(donations),
        'available_count': len(available_donations),
        'claimed_count': len(claimed_donations),
        'urgent_count': len(urgent_available),
        'total_kg': total_kg,
        'total_servings': total_servings,
        'co2_saved_kg': co2_saved_kg
    }
