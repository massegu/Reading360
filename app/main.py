import streamlit as st
import tempfile
import os
from backend.analyze_voice import analyze_audio
from backend.predict_reader import predict_reader
from backend.register_data import save_reading, save_attention
from backend.analyze_attention import calculate_attention_score
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
st.markdown(f"**Nivel:** {current_text['level']}")
st.markdown(f"**Texto:** {current_text['content']}")

# 🎙️ Subir o grabar audio
st.markdown("### Paso 1: Sube tu lectura en voz alta")
audio_file = st.file_uploader("Sube un archivo de audio (.mp3 o .wav)", type=["mp3", "wav"])

if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.type.split('/')[-1]}") as tmp:
        tmp.write(audio_file.read())
        st.session_state.audio_path = tmp.name
    st.audio(st.session_state.audio_path)

# 📊 Analizar voz
if st.session_state.audio_path and st.button("🔍 Analizar lectura"):
    with st.spinner("Analizando con Whisper..."):
        st.session_state.metrics = analyze_audio(st.session_state.audio_path)
        st.success("✅ Análisis completado")

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
        # Cargar puntos de mirada desde attention.json
        try:
            with open("data/attention.json") as f:
                attention_data = json.load(f)
                last_gaze_points = attention_data[-1]["points"] if attention_data else []
                attention_score = calculate_attention_score(last_gaze_points)
        except Exception as e:
            st.warning("⚠️ No se pudo calcular el attention_score")
            attention_score = 0.0
        reading_id = f"r{uuid.uuid4().hex[:6]}"
        save_reading({
            "id": reading_id,
            "user_id": "demo_user",
            "text_id": current_text["id"],
            "words_per_minute": st.session_state.metrics["words_per_minute"],
            "error_rate": st.session_state.metrics.get("error_rate", 0),
            "fluency_score": st.session_state.metrics["fluency_score"],
            "attention_score": attention_score,
            "label": st.session_state.prediction["label"]
    })
    st.success(f"✅ Lectura guardada con attention_score: {attention_score}")


# ➡️ Siguiente texto
if st.session_state.index < len(texts) - 1 and st.button("➡️ Siguiente texto"):
    st.session_state.index += 1
    st.session_state.audio_path = None
    st.session_state.metrics = None
    st.session_state.prediction = None

from streamlit_webrtc import webrtc_streamer
from app.video_stream import FaceMeshTransformer

st.markdown("### 👁️ Seguimiento facial en tiempo real")
webrtc_streamer(key="face-tracker", video_transformer_factory=FaceMeshTransformer)
