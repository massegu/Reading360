from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS
from backend.analyze_voice import analyze_audio
from backend.extract_gaze_metrics import extract_gaze_metrics
from backend.analyze_attention import analyze_visual_metrics
from backend.register_data import save_reading
from backend.register_data import DATA_DIR
import tempfile

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)



@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió archivo de audio"}), 400

    audio_file = request.files["audio"]
    text = request.form.get("text", "")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_file.save(tmp.name)
        audio_path = tmp.name
        try:
            voice_metrics= analyze_audio(audio_path,expected_text=text)
            return jsonify(voice_metrics)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            os.remove(tmp.name)

@app.route("/upload-visual", methods=["POST"])
def upload_visual():
    try:
        data = request.get_json()
        gaze_direction = data.get("gazeDirection")
        #gaze_points = data.get("gazePoints", [])

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
        #gaze_metrics = extract_gaze_metrics(gaze_points)

        # Combinar resultados
        #visual_metrics.update(gaze_metrics)
        visual_metrics["gaze_direction"] = gaze_direction
        visual_metrics["attention_score"] = attention_score

        return jsonify(visual_metrics)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/register-reading", methods=["POST"])
def register_reading():
    try:
        print("🚀 Ruta /register-reading fue alcanzada")
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        # Validación de campos principales
        missing = [k for k in ["session_id", "user_id", "text_id", "label", "voice", "visual"] if k not in data]
        if missing:
            return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

        voice = data["voice"]
        visual = data["visual"] 
        # Validación de subcampos en voice
        voice_required = ["words_per_minute", "error_rate", "fluency_score", "transcription"]
        missing_voice = [k for k in voice_required if k not in voice]
        if missing_voice:
            return jsonify({"error": f"Faltan campos en 'voice': {', '.join(missing_voice)}"}), 400
        # Validación de subcampos en visual
        visual_required = ["attention_score"]
        missing_visual = [k for k in visual_required if k not in visual]
        if missing_visual:
            return jsonify({"error": f"Faltan campos en 'visual': {', '.join(missing_visual)}"}), 400

        reading = {
            "id": data.get("session_id", "unknown"),
            "user_id": data.get("user_id", "anon"),
            "age": data.get("age", ""),
            "sex": data.get("sex", ""),
            "text_id": data.get("text_id", "default"),
            "words_per_minute": voice.get("words_per_minute", 0),
            "error_rate": voice.get("error_rate", 0),
            "fluency_score": voice.get("fluency_score", 0),
            "attention_score": visual.get("attention_score", 0),
            "label": data.get("label", "unlabeled"),
            "transcription": voice.get("transcription", "")
        }
        print("📊 Datos de lectura a registrar:", reading)  # ← Confirmación en terminal
        save_reading(reading)
        
        return jsonify({"status": "✅ Lectura registrada", "id": reading["id"]})
    except Exception as e:
        print("❌ Error en /register-reading:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "✅ Backend activo"

@app.route("/download-readings")
def download_readings():
    return send_from_directory(DATA_DIR, "readings.csv", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)

