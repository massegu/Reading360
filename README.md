# Reading360

Reading360 es una aplicación educativa que evalúa la calidad lectora de una persona mediante voz, mirada y tiempo de lectura. Utiliza inteligencia artificial para clasificar tipos de lectores y generar métricas como velocidad, fluidez, atención y precisión.

## Características

- Transcripción de voz con Whisper
- Seguimiento ocular con MediaPipe
- Registro de datos en CSV y JSON
- Clasificación automática con modelos de machine learning
- Interfaz visual con Streamlit

## Requisitos

- Python 3.8+
- Instalar dependencias con `pip install -r requirements.txt`

## Estructura

- `app/`: interfaz visual
- `backend/`: procesamiento de voz y mirada
- `model/`: entrenamiento y predicción
- `data/`: almacenamiento de lecturas

## Cómo iniciar

```bash
streamlit run app/main.py
