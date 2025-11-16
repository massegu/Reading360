import csv
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
READINGS_PATH = os.path.join(DATA_DIR, "readings.csv")
ATTENTION_PATH = os.path.join(DATA_DIR, "attention.json")

def save_reading(data):
    """
    Guarda una lectura en readings.csv
    """
    print("📥 save_reading fue llamado con:", data)
    file_exists = os.path.isfile(READINGS_PATH)

    # Sanear el campo transcription
    transcription = data.get("transcription", "")
    if transcription:
        transcription = transcription.replace("\n", " ").replace('"', "'").strip()

    values = [
        data.get("id", ""),
        data.get("user_id", ""),
        data.get("text_id", ""),
        data.get("words_per_minute", 0),
        data.get("error_rate", 0),
        data.get("fluency_score", 0),
        data.get("attention_score", 0),
        data.get("label", ""),
        transcription
    ]
    print("📦 Valores recibidos para guardar:", values)
    print("🔢 Longitud:", len(values))

    if len(values) != 9:
        print("❌ Error: número incorrecto de campos:", len(values), values)
        return
    else:
        print("✅ Número correcto de campos. Escribiendo en CSV")
    with open(READINGS_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "id", "user_id", "text_id",
                "words_per_minute", "error_rate",
                "fluency_score", "attention_score", "label",
                "transcription"
            ])
        writer.writerow(values)

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
