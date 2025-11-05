from flask import Flask, request, jsonify
from backend.analyze_voice import analyze_audio
import tempfile
import os
from backend.analyze_attention import analyze_visual_metrics  # ← asegúrate de tener esta función
import json


app = Flask(__name__)

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió archivo de audio"}), 400

    audio_file = request.files["audio"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_file.save(tmp.name)
        try:
            metrics = analyze_audio(tmp.name)
            return jsonify(metrics)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            os.remove(tmp.name)

if __name__ == "__main__":
    app.run(debug=True)

app = Flask(__name__)

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió archivo de audio"}), 400

    audio_file = request.files["audio"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_file.save(tmp.name)
        try:
            metrics = analyze_audio(tmp.name)
            return jsonify(metrics)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            os.remove(tmp.name)

@app.route("/upload-visual", methods=["POST"])
def upload_visual():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos visuales"}), 400

        # Aquí llamas a tu función de análisis visual
        visual_metrics = analyze_visual_metrics(data)

        return jsonify(visual_metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

from backend.register_data import save_reading

@app.route("/register-reading", methods=["POST"])
def register_reading():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        voice = data.get("voice", {})
        visual = data.get("visual", {})

        reading = {
            "id": data.get("session_id", "unknown"),
            "user_id": data.get("user_id", "anon"),
            "text_id": data.get("text_id", "default"),
            "words_per_minute": voice.get("words_per_minute", 0),
            "error_rate": voice.get("error_rate", 0),  # si no lo tienes aún, pon 0
            "fluency_score": voice.get("fluency_score", 0),
            "attention_score": visual.get("attention_score", 0),
            "label": data.get("label", "unlabeled"),
            "gaze_path_length": visual.get("gaze_path_length", 0),
            "fixation_count": visual.get("fixation_count", 0),
            "transcription": voice.get("transcription", "")
        }

        save_reading(reading)
        return jsonify({"status": "✅ Lectura registrada", "id": reading["id"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
