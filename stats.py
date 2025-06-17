# === stats.py ===
import os
import json

STATS_FILE = 'stats.json'

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {'total_images': 0, 'users': {}, 'animal_count': {}}
    with open(STATS_FILE, 'r') as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)