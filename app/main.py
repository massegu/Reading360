import streamlit as st
import tempfile
import os
from backend.analyze_voice import analyze_audio
from backend.predict_reader import predict_reader

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

# 🧠 Mostrar predicción
if st.session_state.prediction:
    st.markdown("### Clasificación del lector")
    st.success(f"📌 Tipo de lector: **{st.session_state.prediction['label']}**")
    st.caption(f"Confianza del modelo: {st.session_state.prediction['confidence']:.2%}")

# ➡️ Siguiente texto
if st.session_state.index < len(texts) - 1 and st.button("➡️ Siguiente texto"):
    st.session_state.index += 1
    st.session_state.audio_path = None
    st.session_state.metrics = None
    st.session_state.prediction = None
