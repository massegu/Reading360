import cv2
import mediapipe as mp
from streamlit_webrtc import VideoProcessorBase

class FaceMeshTransformer(VideoProcessorBase):
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False)
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1)

    def recv(self, frame):
        try:
            img = frame.to_ndarray(format="bgr24")
            results = self.face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    self.mp_drawing.draw_landmarks(
                        image=img,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=self.drawing_spec,
                        connection_drawing_spec=self.drawing_spec
                    )
            return img
        except Exception as e:
            print("Error en transform:", e)
            return frame
