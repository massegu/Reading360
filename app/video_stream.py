import cv2
import av
import mediapipe as mp
from streamlit_webrtc import VideoTransformerBase
from backend.register_data import save_attention
import time

mp_face_mesh = mp.solutions.face_mesh

class FaceMeshTransformer(VideoTransformerBase):
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh()
        self.gaze_points = []
        self.last_save_time = time.time()

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        results = self.face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for lm in face_landmarks.landmark:
                    x = int(lm.x * img.shape[1])
                    y = int(lm.y * img.shape[0])
                    self.gaze_points.append({"x": x, "y": y, "t": time.time()})
                    cv2.circle(img, (x, y), 1, (0, 255, 0), -1)

        # Guardar puntos cada 5 segundos
        if time.time() - self.last_save_time > 5 and self.gaze_points:
            save_attention(self.gaze_points)
            self.gaze_points = []
            self.last_save_time = time.time()

        return img
