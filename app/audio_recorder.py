from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import wave
import tempfile

class AudioProcessor:
    def __init__(self):
        self.frames = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame

def record_audio():
    processor = AudioProcessor()
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=lambda: processor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )

    audio_path = None
    if webrtc_ctx.audio_receiver and webrtc_ctx.state.playing:
        if processor.frames:
            audio_data = np.concatenate(processor.frames, axis=0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                with wave.open(tmp.name, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(audio_data.tobytes())
                audio_path = tmp.name
    return audio_path
