import math

def calculate_attention_score(gaze_points):
    """
    Calcula un attention_score entre 0 y 1 basado en la dispersión de la mirada.
    """
    if not gaze_points:
        return 0.0

    xs = [p["x"] for p in gaze_points]
    ys = [p["y"] for p in gaze_points]

    # Centro de la mirada
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)

    # Dispersión (desviación estándar euclidiana)
    dispersion = sum(math.sqrt((x - mean_x)**2 + (y - mean_y)**2) for x, y in zip(xs, ys)) / len(xs)

    # Normalizar: cuanto menor la dispersión, mayor la atención
    max_dispersion = 300  # ajustable según resolución
    score = max(0.0, min(1.0, 1 - dispersion / max_dispersion))
    return round(score, 3)

from .analyze_attention import calculate_attention_score

def analyze_visual_metrics(data):
    """
    Recibe coordenadas faciales y calcula métricas de atención.
    """
    try:
        # Espera una lista de puntos de mirada: [{"x": ..., "y": ...}, ...]
        gaze_points = data.get("gazePoints", [])
        score = calculate_attention_score(gaze_points)

        return {
            "attention_score": score,
            "num_points": len(gaze_points)
        }
    except Exception as e:
        return {"error": str(e)}

