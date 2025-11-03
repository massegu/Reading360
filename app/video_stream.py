import cv2
import av
import mediapipe as mp
from streamlit_webrtc import VideoTransformerBase

mp_face_mesh = mp.solutions.face_mesh

class FaceMeshTransformer(VideoTransformerBase):
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh()

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        results = self.face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for lm in face_landmarks.landmark:
                    x = int(lm.x * img.shape[1])
                    y = int(lm.y * img.shape[0])
                    cv2.circle(img, (x, y), 1, (0, 255, 0), -1)

        return img
