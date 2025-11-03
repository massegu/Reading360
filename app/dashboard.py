import streamlit as st
import json
import pandas as pd

def show_readings_dashboard():
    st.markdown("## 📂 Lecturas guardadas")

    # Cargar datos
    try:
        with open("data/readings.json") as f:
            readings = json.load(f)
    except Exception as e:
        st.error("❌ No se pudieron cargar las lecturas guardadas")
        return

    if not readings:
        st.info("ℹ️ No hay lecturas guardadas todavía.")
        return

    # Convertir a DataFrame
    df = pd.DataFrame(readings)

    # 🎛️ Filtros
    niveles = df["text_id"].map(lambda tid: next((t["level"] for t in TEXTOS if t["id"] == tid), "Desconocido"))
    df["Nivel"] = niveles
    tipo_lector = st.multiselect("📌 Filtrar por tipo de lector", options=df["label"].unique())
    nivel_lector = st.multiselect("📚 Filtrar por nivel de texto", options=df["Nivel"].unique())

    # Aplicar filtros
    if tipo_lector:
        df = df[df["label"].isin(tipo_lector)]
    if nivel_lector:
        df = df[df["Nivel"].isin(nivel_lector)]

    # 📊 Mostrar tabla
    st.dataframe(df[[
        "id", "user_id", "text_id", "Nivel", "label",
        "words_per_minute", "error_rate", "fluency_score",
        "attention_score", "gaze_path_length", "fixation_count"
    ]].rename(columns={
        "id": "ID",
        "user_id": "Usuario",
        "text_id": "Texto",
        "label": "Tipo de lector",
        "words_per_minute": "Palabras/min",
        "error_rate": "Tasa de error",
        "fluency_score": "Fluidez",
        "attention_score": "Atención",
        "gaze_path_length": "Recorrido visual",
        "fixation_count": "Fijaciones"
    }), use_container_width=True)

# 🔁 Textos de lectura para mapear niveles
TEXTOS = [
    {"id": "txt001", "level": "Fácil", "content": "El sol brilla en el cielo azul."},
    {"id": "txt002", "level": "Intermedio", "content": "Los animales del bosque se reúnen cada mañana para buscar alimento."},
    {"id": "txt003", "level": "Difícil", "content": "La neuroplasticidad permite que el cerebro reorganice sus conexiones sinápticas en respuesta a estímulos."}
]
