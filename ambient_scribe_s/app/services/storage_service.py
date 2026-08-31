import json
import os

DB_FILE = "clinical_records.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("records", [])
    return []


def save_db(records):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"records": records}, f, indent=4)