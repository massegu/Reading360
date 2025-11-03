import math

def gaze_path_length(gaze_points):
    """
    Calcula la distancia total recorrida por la mirada.
    """
    if len(gaze_points) < 2:
        return 0.0

    total_distance = 0.0
    for i in range(1, len(gaze_points)):
        x1, y1 = gaze_points[i - 1]["x"], gaze_points[i - 1]["y"]
        x2, y2 = gaze_points[i]["x"], gaze_points[i]["y"]
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        total_distance += dist

    return round(total_distance, 2)


def fixation_count(gaze_points, threshold=15):
    """
    Cuenta cuántas veces la mirada se estabiliza (fijación).
    Se considera fijación si el movimiento entre puntos consecutivos es menor al umbral.
    """
    if len(gaze_points) < 2:
        return 0

    count = 0
    for i in range(1, len(gaze_points)):
        x1, y1 = gaze_points[i - 1]["x"], gaze_points[i - 1]["y"]
        x2, y2 = gaze_points[i]["x"], gaze_points[i]["y"]
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if dist < threshold:
            count += 1

    return count


def extract_gaze_metrics(gaze_points):
    """
    Devuelve todas las métricas de mirada en un diccionario.
    """
    return {
        "gaze_path_length": gaze_path_length(gaze_points),
        "fixation_count": fixation_count(gaze_points)
    }
