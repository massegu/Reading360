from flask import Flask, request, jsonify
from backend.analyze_voice import analyze_audio
from backend.analyze_attention import analyze_visual_metrics
from backend.register_data import save_reading
import tempfile
import os

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
        gaze_direction = data.get("gazeDirection")

        # Calcular atención básica
        if gaze_direction == "centro":
            attention_score = 1.0
        elif gaze_direction =="izquierda":
            attention_score = 0.5
        elif gaze_direction =="derecha":
            attention_score = -0.5
        else:
            attention_score = 0.0

        # Análisis visual adicional
        visual_metrics = analyze_visual_metrics(data)

        # Combinar resultados
        visual_metrics["gaze_direction"] = gaze_direction
        visual_metrics["attention_score"] = attention_score

        return jsonify(visual_metrics)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
            "error_rate": voice.get("error_rate", 0),
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

@app.route("/", methods=["GET"])
def home():
    return "✅ Reading360 backend activo"

if __name__ == "__main__":
    app.run(debug=True)

