import streamlit as st
import tempfile
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from streamlit_webrtc import webrtc_streamer
from streamlit_webrtc import WebRtcMode
from app.video_stream import FaceMeshTransformer
from audio_recorder import AudioProcessor
from backend.analyze_voice import analyze_audio
from backend.predict_reader import predict_reader
from backend.register_data import save_reading, save_attention
from backend.analyze_attention import calculate_attention_score
from backend.extract_gaze_metrics import extract_gaze_metrics
from app.dashboard import show_readings_dashboard
import json
import uuid

st.set_page_config(page_title="Reading360", layout="centered")
st.sidebar.title("🧭 Navegación")
vista = st.sidebar.radio("Selecciona una vista:", ["Evaluación lectora", "Historial de lecturas"])

if vista == "Evaluación lectora":
    # tu código actual aquí


# 📚 Textos de lectura
    texts = [
    {"id": "txt001", "level": "Fácil", "content": "El sol brilla en el cielo azul."},
    {"id": "txt002", "level": "Intermedio", "content": "Los animales del bosque se reúnen cada mañana para buscar alimento."},
    {"id": "txt003", "level": "Difícil", "content": "La neuroplasticidad permite que el cerebro reorganice sus conexiones sinápticas en respuesta a estímulos."}
]

# 🔁 Estado de sesión
if "index" not in st.session_state:
    st.session_state.index = 0
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "prediction" not in st.session_state:
    st.session_state.prediction = None

# 🧠 Título
st.title("📖 Reading360")
st.subheader("Evaluación lectora con voz, mirada y tiempo")

# 📝 Mostrar texto actual
current_text = texts[st.session_state.index]
level_colors = {
    "Fácil": "#2E8B57",       # verde
    "Intermedio": "#1E90FF",  # azul
    "Difícil": "#B22222"      # rojo
}
color = level_colors.get(current_text["level"], "#333")

st.markdown(f"**Nivel:** {current_text['level']}")
st.markdown(
    f"<div style='font-size:28px; font-weight:500; line-height:1.6; color:{color}'>{current_text['content']}</div>",
    unsafe_allow_html=True
)

# 🎙️ Paso 1: Graba tu lectura en voz alta
st.markdown("### Paso 1: Graba tu lectura en voz alta")

# Inicializar el procesador si no existe
if "audio_processor" not in st.session_state:
    st.session_state.audio_processor = AudioProcessor()

# Mostrar el componente de grabación
webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=lambda: st.session_state.audio_processor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# Procesar el audio si hay datos
if webrtc_ctx.state.playing and st.session_state.audio_processor.frames:
    if st.button("📥 Procesar audio grabado"):
        import numpy as np
        import wave

        audio_data = np.concatenate(st.session_state.audio_processor.frames, axis=0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(48000)
                wf.writeframes(audio_data.tobytes())
            st.session_state.audio_path = tmp.name
            st.audio(tmp.name)
            st.success("✅ Audio grabado correctamente")


# 👁️ Paso 2: Seguimiento facial
st.markdown("### 👁️ Seguimiento facial en tiempo real")
webrtc_streamer(
    key="face-tracker", 
    video_processor_factory=FaceMeshTransformer,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)
st.info("📸 Si no ves tu cara, asegúrate de que la cámara está activada y permitida en el navegador.")

# 📊 Paso 3: Análisis de voz
st.write(f"📎 Audio path actual: {st.session_state.audio_path}")
if isinstance(st.session_state.audio_path, str) and st.session_state.audio_path.endswith(".wav"):
    st.markdown("### Paso 3: Resultados del análisis")
    with st.spinner("Analizando con Whisper..."):
        try:
            st.session_state.metrics = analyze_audio(st.session_state.audio_path)
            st.success("✅ Análisis completado")
        except Exception as e:
            st.error(f"❌ Error en el análisis de audio: {e}")

# 📈 Mostrar métricas
if st.session_state.metrics:
    st.markdown("### Resultados de la lectura")
    st.write(st.session_state.metrics)

    if st.button("🤖 Clasificar tipo de lector"):
        st.session_state.prediction = predict_reader(st.session_state.metrics)

# 🧠 Mostrar predicción y guardar lectura
if st.session_state.prediction:
    st.markdown("### Clasificación del lector")
    st.success(f"📌 Tipo de lector: **{st.session_state.prediction['label']}**")
    st.caption(f"Confianza del modelo: {st.session_state.prediction['confidence']:.2%}")

if st.session_state.metrics and st.session_state.prediction:
    if st.button("💾 Guardar lectura"):
        attention_score = 0.0
        gaze_metrics = {"gaze_path_length": 0.0, "fixation_count": 0}
        attention_data = []

    if os.path.exists("data/attention.json"):
        try:
            with open("data/attention.json") as f:
                content = f.read().strip()
                if content:
                    attention_data = json.loads(content)
                    last_gaze_points = attention_data[-1]["points"] if attention_data else []
                    attention_score = calculate_attention_score(last_gaze_points)
                    gaze_metrics = extract_gaze_metrics(last_gaze_points)
                else:
                    st.warning("⚠️ El archivo attention.json está vacío")
        except Exception as e:
            st.warning(f"⚠️ No se pudo leer el archivo attention.json: {e}")
    else:
        st.warning("⚠️ El archivo attention.json no existe")
    
        reading_id = f"r{uuid.uuid4().hex[:6]}"
        save_reading({
            "id": reading_id,
            "user_id": "demo_user",
            "text_id": current_text["id"],
            "words_per_minute": st.session_state.metrics["words_per_minute"],
            "error_rate": st.session_state.metrics.get("error_rate", 0),
            "fluency_score": st.session_state.metrics["fluency_score"],
            "attention_score": attention_score,
            "label": st.session_state.prediction["label"],
            "gaze_path_length": gaze_metrics["gaze_path_length"],
            "fixation_count": gaze_metrics["fixation_count"],
            "transcription": st.session_state.metrics["transcription"],
        })
        st.success(f"✅ Lectura guardada con attention_score: {attention_score}")

elif vista == "Historial de lecturas":
    show_readings_dashboard()
