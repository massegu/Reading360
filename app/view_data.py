import pandas as pd
import streamlit as st

def show_readings_dashboard():
    st.markdown("## 📊 Panel de lecturas guardadas")

    try:
        df = pd.read_csv("data/readings.csv")
    except FileNotFoundError:
        st.warning("No se encontró el archivo readings.csv")
        return

    # 🎯 Filtros
    lector_tipo = st.selectbox("Filtrar por tipo de lector", options=["Todos"] + sorted(df["label"].unique()))
    nivel_texto = st.selectbox("Filtrar por nivel de texto", options=["Todos", "Fácil", "Intermedio", "Difícil"])

    # 🧹 Aplicar filtros
    if lector_tipo != "Todos":
        df = df[df["label"] == lector_tipo]
    if nivel_texto != "Todos":
        df = df[df["text_id"].str.contains(nivel_texto.lower())]

    # 📈 Mostrar tabla
    st.dataframe(df)

    # 📊 Métricas agregadas
    st.markdown("### Métricas promedio")
    st.write(df[["words_per_minute", "error_rate", "fluency_score", "attention_score"]].mean().round(2))
