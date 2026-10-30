"""
Food Rescue Revolution - ML Dataset Generator
Generates realistic food spoilage decay data based on food science Arrhenius kinetics and Q10 temperature coefficient.
"""

import csv
import math
import random

random.seed(42)

CATEGORIES = {
    'cooked_meals': {'base_life': 6.0, 'temp_sensitivity': 1.6, 'moisture_sens': 1.2},
    'dairy': {'base_life': 5.0, 'temp_sensitivity': 1.9, 'moisture_sens': 1.4},
    'bakery': {'base_life': 36.0, 'temp_sensitivity': 1.1, 'moisture_sens': 1.8},
    'fresh_produce': {'base_life': 48.0, 'temp_sensitivity': 1.3, 'moisture_sens': 1.1},
    'packaged_goods': {'base_life': 72.0, 'temp_sensitivity': 1.05, 'moisture_sens': 1.0}
}

FOOD_TYPES = ['veg', 'non_veg', 'vegan']
STORAGE_CONDITIONS = {
    'ambient_room': 1.0,
    'refrigerated': 3.2,
    'thermal_insulated': 1.8
}
PACKAGING_TYPES = {
    'open_container': 0.7,
    'plastic_wrap': 1.0,
    'sealed_foil': 1.3,
    'airtight_vacuum': 1.7
}

DATASET_FILE = 'ml/dataset.csv'
NUM_SAMPLES = 5000

with open(DATASET_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'sample_id',
        'category',
        'food_type',
        'ambient_temp_c',
        'humidity_percent',
        'storage_condition',
        'packaging_type',
        'prepared_hours_ago',
        'initial_weight_kg',
        'microbial_cfu_log',
        'remaining_shelf_life_hours',
        'safety_status',
        'urgency_tier'
    ])

    for i in range(1, NUM_SAMPLES + 1):
        cat = random.choice(list(CATEGORIES.keys()))
        cat_props = CATEGORIES[cat]
        food_type = random.choice(FOOD_TYPES)
        if cat in ['dairy', 'bakery', 'fresh_produce']:
            food_type = 'veg' if cat != 'fresh_produce' else 'vegan'

        # Realistic feature distributions
        ambient_temp = round(random.gauss(28.0, 6.0), 1)
        ambient_temp = max(15.0, min(45.0, ambient_temp))

        humidity = round(random.uniform(30.0, 90.0), 1)
        storage = random.choices(
            list(STORAGE_CONDITIONS.keys()),
            weights=[0.55, 0.25, 0.20]
        )[0]
        packaging = random.choices(
            list(PACKAGING_TYPES.keys()),
            weights=[0.25, 0.40, 0.25, 0.10]
        )[0]

        # Max hours based on category
        max_prep = 12.0 if cat in ['cooked_meals', 'dairy'] else (30.0 if cat == 'bakery' else 40.0)
        prepared_hours = round(random.uniform(0.5, max_prep), 1)
        weight_kg = round(random.uniform(3.0, 80.0), 1)

        # Base shelf life calculation via Arrhenius-derived biological decay formula
        base_life = cat_props['base_life']
        if food_type == 'non_veg':
            base_life *= 0.75

        # Temperature decay factor (Q10 rule: spoilage rate doubles every 10 deg above 4C)
        effective_temp = 4.0 if storage == 'refrigerated' else (ambient_temp - 5.0 if storage == 'thermal_insulated' else ambient_temp)
        temp_factor = math.pow(cat_props['temp_sensitivity'], (effective_temp - 20.0) / 10.0)
        temp_factor = max(0.3, temp_factor)

        # Moisture factor
        humidity_factor = 1.0 + (humidity - 50.0) / 150.0 * cat_props['moisture_sens']

        # Storage & Packaging multi-factor
        preservation_multiplier = STORAGE_CONDITIONS[storage] * PACKAGING_TYPES[packaging]

        total_shelf_life = (base_life * preservation_multiplier) / (temp_factor * humidity_factor)
        # Add slight natural biological variance (+- 7%)
        noise = random.gauss(1.0, 0.05)
        total_shelf_life *= noise

        remaining_hours = max(0.0, total_shelf_life - prepared_hours)
        remaining_hours = round(remaining_hours, 2)

        # Microbial CFU count estimation (Log10 scale: <4 safe, 4-6 warning, >6 spoiled)
        decay_progress = min(2.0, prepared_hours / max(1.0, total_shelf_life))
        cfu_log = round(2.0 + (decay_progress * 4.5) + random.uniform(-0.3, 0.3), 2)
        cfu_log = max(1.5, min(8.5, cfu_log))

        if remaining_hours <= 0.2 or cfu_log >= 6.0:
            safety_status = 'Spoiled'
            urgency_tier = 'CRITICAL_EXPIRED'
        elif remaining_hours <= 2.5:
            safety_status = 'Urgent'
            urgency_tier = 'RED_ALERT'
        elif remaining_hours <= 6.0:
            safety_status = 'Moderate'
            urgency_tier = 'HIGH_PRIORITY'
        else:
            safety_status = 'Safe'
            urgency_tier = 'NORMAL'

        writer.writerow([
            f'SMP-{i:05d}',
            cat,
            food_type,
            ambient_temp,
            humidity,
            storage,
            packaging,
            prepared_hours,
            weight_kg,
            cfu_log,
            remaining_hours,
            safety_status,
            urgency_tier
        ])

print(f"Generated {NUM_SAMPLES} verified food spoilage decay records in {DATASET_FILE}.")
