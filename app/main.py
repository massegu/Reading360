import streamlit as st
import tempfile
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from streamlit_webrtc import webrtc_streamer
from app.video_stream import FaceMeshTransformer
from audio_recorder import record_audio
from backend.analyze_voice import analyze_audio
from backend.predict_reader import predict_reader
from backend.register_data import save_reading, save_attention
from backend.analyze_attention import calculate_attention_score
from backend.extract_gaze_metrics import extract_gaze_metrics
from app.dashboard import show_readings_dashboard
import json
import uuid

st.set_page_config(page_title="Reading360", layout="centered")

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

# 🎙️ Subir o grabar audio
st.markdown("### Paso 1: Graba tu lectura en voz alta")

audio_path = record_audio()
if audio_path:
    st.session_state.audio_path = audio_path
    st.audio(audio_path)
    st.success("✅ Audio grabado correctamente")

    st.markdown("### 👁️ Seguimiento facial en tiempo real")
    webrtc_streamer(key="face-tracker", video_transformer_factory=FaceMeshTransformer)
    st.info("📸 Si no ves tu cara, asegúrate de que la cámara está activada y permitida en el navegador.")


    # 📊 Analizar voz automáticamente
    st.markdown("### Paso 2: Resultados del análisis")
    with st.spinner("Analizando con Whisper..."):
        try:
            st.session_state.metrics = analyze_audio(audio_path)
            st.success("✅ Análisis completado")
        except Exception as e:
            st.error("❌ Error al analizar el audio")

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

    if st.button("💾 Guardar lectura"):
        attention_score = 0.0
        gaze_metrics = {"gaze_path_length": 0.0, "fixation_count": 0}

        # Cargar puntos de mirada desde attention.json
        try:
            with open("data/attention.json") as f:
                attention_data = json.load(f)
                last_gaze_points = attention_data[-1]["points"] if attention_data else []
                attention_score = calculate_attention_score(last_gaze_points)
                gaze_metrics = extract_gaze_metrics(last_gaze_points)
        except Exception as e:
            st.warning("⚠️ No se pudo calcular el attention_score")
            attention_score = 0.0
            gaze_metrics = {"gaze_path_length": 0.0, "fixation_count": 0}

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
            "transcription": st.session_state.transcription,

    })
    st.success(f"✅ Lectura guardada con attention_score: {attention_score}")


# ➡️ Siguiente texto
if st.session_state.index < len(texts) - 1 and st.button("➡️ Siguiente texto"):
    st.session_state.index += 1
    st.session_state.audio_path = None
    st.session_state.metrics = None
    st.session_state.prediction = None

if st.checkbox("📂 Ver lecturas guardadas"):
    show_readings_dashboard()
