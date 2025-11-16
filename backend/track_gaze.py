import cv2
import mediapipe as mp
from backend.extract_gaze_metrics import extract_gaze_metrics

def track_gaze_from_camera():
    """
    Muestra puntos faciales en tiempo real desde la cámara y calcula métricas de mirada.
    """
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh()
    cap = cv2.VideoCapture(0)

    gaze_points = []

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                gaze_points = []  # Reinicia en cada frame

                for lm in face_landmarks.landmark:
                    x = int(lm.x * frame.shape[1])
                    y = int(lm.y * frame.shape[0])
                    gaze_points.append({"x": x, "y": y})
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

                # Calcular métricas de mirada
                metrics = extract_gaze_metrics(gaze_points)
                print("📊 Métricas de mirada:", metrics)

                # Mostrar métricas en pantalla
                cv2.putText(frame, f"Gaze Path: {metrics['gaze_path_length']}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, f"Fixations: {metrics['fixation_count']}", (10, 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Reading360 - Seguimiento ocular", frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
