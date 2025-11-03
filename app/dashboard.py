import streamlit as st
import json
import pandas as pd
import difflib

TEXTOS = [
    {"id": "txt001", "level": "Fácil", "content": "El sol brilla en el cielo azul."},
    {"id": "txt002", "level": "Intermedio", "content": "Los animales del bosque se reúnen cada mañana para buscar alimento."},
    {"id": "txt003", "level": "Difícil", "content": "La neuroplasticidad permite que el cerebro reorganice sus conexiones sinápticas en respuesta a estímulos."}
]

def comparar_textos(original, transcripcion):
    original_words = original.lower().split()
    transcribed_words = transcripcion.lower().split()
    diff = difflib.ndiff(original_words, transcribed_words)

    omisiones = []
    inserciones = []

    for d in diff:
        if d.startswith("- "):
            omisiones.append(d[2:])
        elif d.startswith("+ "):
            inserciones.append(d[2:])
    return omisiones, inserciones

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

    # 📤 Exportar a CSV
    st.markdown("### 📤 Exportar lecturas a CSV")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar CSV",
        data=csv,
        file_name="lecturas_guardadas.csv",
        mime="text/csv"
    )

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

    # 📈 Visualizaciones
    st.markdown("## 📈 Visualizaciones")

    st.markdown("### 🧠 Distribución de tipos de lector")
    lector_counts = df["label"].value_counts()
    st.bar_chart(lector_counts)

    st.markdown("### 👁️ Atención promedio por nivel de texto")
    nivel_attention = df.groupby("Nivel")["attention_score"].mean()
    st.bar_chart(nivel_attention)

    st.markdown("### 🔁 Relación entre fluidez y tasa de error")
    st.scatter_chart(df[["fluency_score", "error_rate"]])

    # 🔍 Selección y comparación
    st.markdown("## 🔍 Seleccionar una lectura para ver detalles")
    lectura_ids = df["id"].tolist()
    selected_id = st.selectbox("Selecciona una lectura por ID", options=lectura_ids)

    if selected_id:
        lectura = df[df["id"] == selected_id].iloc[0]
        texto_original = next((t["content"] for t in TEXTOS if t["id"] == lectura["text_id"]), "")
        transcripcion = lectura.get("transcription", "")

        st.markdown("### 📖 Texto original")
        st.markdown(f"<div style='font-size:20px; color:#2E8B57'>{texto_original}</div>", unsafe_allow_html=True)

        st.markdown("### 🗣️ Transcripción del lector")
        st.markdown(f"<div style='font-size:20px; color:#1E90FF'>{transcripcion}</div>", unsafe_allow_html=True)

        omisiones, inserciones = comparar_textos(texto_original, transcripcion)

        st.markdown("### 🔍 Comparación de lectura")
        st.markdown(f"🔴 **Omisiones:** {', '.join(omisiones) if omisiones else 'Ninguna'}")
        st.markdown(f"🟡 **Inserciones:** {', '.join(inserciones) if inserciones else 'Ninguna'}")

