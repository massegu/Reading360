import csv
import json
import os
from datetime import datetime

DATA_DIR = "data"
READINGS_PATH = os.path.join(DATA_DIR, "readings.csv")
ATTENTION_PATH = os.path.join(DATA_DIR, "attention.json")

def save_reading(data):
    """
    Guarda una lectura en readings.csv
    """
    file_exists = os.path.isfile(READINGS_PATH)
    with open(READINGS_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "id", "user_id", "text_id",
                "words_per_minute", "error_rate",
                "fluency_score", "attention_score", "label",
                "gaze_path_length", "fixation_count"
            ])
        writer.writerow([
            data["id"],
            data["user_id"],
            data["text_id"],
            data["words_per_minute"],
            data["error_rate"],
            data["fluency_score"],
            data["attention_score"],
            data["label"],
            data["gaze_path_length"],
            data["fixation_count"]
        ])

def save_attention(gaze_points):
    """
    Guarda coordenadas de mirada en attention.json
    """
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "points": gaze_points
    }

    try:
        with open(ATTENTION_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(entry)

    with open(ATTENTION_PATH, "w") as f:
        json.dump(data, f, indent=2)
