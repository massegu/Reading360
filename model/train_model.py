import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

DATA_PATH = "data/readings.csv"
MODEL_PATH = "model/model.pkl"

def train_model():
    # 📥 Cargar datos
    if not os.path.exists(DATA_PATH):
        print("❌ No se encontró readings.csv en la carpeta data/")
        return

    df = pd.read_csv(DATA_PATH)

    # 🧹 Verificar columnas necesarias
    required_columns = [
        "words_per_minute", "error_rate", "fluency_score", "attention_score",
        "gaze_path_length", "fixation_count", "label"
    ]

    if not all(col in df.columns for col in required_columns):
        print("❌ El archivo CSV no contiene todas las columnas necesarias")
        return

    # 🎯 Features y etiquetas
    X = df[[
        "words_per_minute",
        "error_rate",
        "fluency_score",
        "attention_score",
        "gaze_path_length",
        "fixation_count"
    ]]
    y = df["label"]

    # 🔀 Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 🧠 Entrenar modelo
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 📊 Evaluar
    y_pred = model.predict(X_test)
    print("📈 Reporte de clasificación:")
    print(classification_report(y_test, y_pred))

    # 💾 Guardar modelo
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"✅ Modelo guardado en {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
