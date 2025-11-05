import whisper
from pydub import AudioSegment
import tempfile
import os

# Cargar el modelo Whisper una sola vez
model = whisper.load_model("base")

def analyze_audio(audio_path):
    """
    Transcribe el audio y calcula métricas de lectura.
    """
    try:
        # Convertir a WAV si es necesario
        if not audio_path or not isinstance(audio_path, str) or not audio_path.endswith(".wav"):
            sound = AudioSegment.from_file(audio_path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                sound.export(tmp_wav.name, format="wav")
                audio_path = tmp_wav.name

        # Transcribir con Whisper
        result = model.transcribe(audio_path)
        text = result.get("text", "")
        segments = result.get("segments", [])
        duration = segments[-1]["end"] if segments else 0

        # Calcular palabras por minuto
        words = len(text.split())
        wpm = round(words / (duration / 60), 2) if duration > 0 else 0

        # Fluidez básica
        fluency_score = round(min(wpm / 150, 1.0), 2)  # escala de 0 a 1

        return {
            "transcription": text,
            "duration": round(duration, 2),
            "words": words,
            "words_per_minute": wpm,
            "fluency_score": fluency_score
        }

    except Exception as e:
        print("❌ Error al analizar el audio:", e)
        return {
            "error": str(e)
        }

