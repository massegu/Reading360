import os
import pickle

MODEL_PATH = "model/model.pkl"

def predict_reader(metrics):
    """
    Predice el tipo de lector usando el modelo entrenado.
    """
    if not os.path.exists(MODEL_PATH):
        return {
            "label": "desconocido",
            "confidence": 0.0,
            "note": "Modelo no entrenado aún. Ejecuta train_model.py para entrenarlo con datos reales."
        }

    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

        # Extraer características relevantes
        features = [
            metrics.get("words_per_minute", 0),
            metrics.get("error_rate", 0),
            metrics.get("fluency_score", 0),
            metrics.get("attention_score", 0)
        ]

        prediction = model.predict([features])[0]
        confidence = max(model.predict_proba([features])[0])

        return {
            "label": prediction,
            "confidence": round(confidence, 4)
        }

    except Exception as e:
        print("❌ Error en la predicción:", e)
        return {
            "label": "error",
            "confidence": 0.0,
            "note": str(e)
        }
