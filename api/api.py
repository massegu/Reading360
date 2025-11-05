from flask import Flask, request, jsonify
from backend.analyze_voice import analyze_audio
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

if __name__ == "__main__":
    app.run(debug=True)
