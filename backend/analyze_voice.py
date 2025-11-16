import whisper
from pydub import AudioSegment
import tempfile
import os

_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

from difflib import SequenceMatcher

def compute_error_rate(transcribed, expected):
    ratio = SequenceMatcher(None, transcribed.lower(), expected.lower()).ratio()
    return round(1 - ratio, 2)

def analyze_audio(audio_path, expected_text=""):
    """
    Transcribe el audio y calcula métricas de lectura.
    """
    model = get_model()
    try:
        # Convertir a WAV si es necesario
        if not isinstance(audio_path, str) or not audio_path.endswith(".wav"):
            sound = AudioSegment.from_file(audio_path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                sound.export(tmp_wav.name, format="wav")
                audio_path = tmp_wav.name

        # Transcribir con Whisper
        result = model.transcribe(audio_path)
        text = result.get("text", "")
        error_rate = compute_error_rate(text, expected_text)
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
            "fluency_score": fluency_score,
            "error_rate": error_rate
        }

    except Exception as e:
        print("❌ Error al analizar el audio:", e)
        return {
            "error": str(e)
        }

