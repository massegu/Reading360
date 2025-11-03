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
