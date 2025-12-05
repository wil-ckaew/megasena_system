from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import os

MODEL_PATH = "megasena_rf_model.joblib"
CSV_PATH = "resultados_megasena.csv"
app = Flask(__name__)

# -------------------------------
# 🔹 Função "bola do dia"
# -------------------------------
def gerar_combinacoes_pela_bola(dia_base: int):
    base = dia_base % 10
    combinacoes = []
    for i in range(6):
        # Soma cumulativa + último dígito da bola
        val = (base + (i*4) + (i*3)) % 60
        if val == 0:
            val = 60
        combinacoes.append(val)
    combinacoes = sorted(list(set(combinacoes)))[:6]
    return combinacoes

# -------------------------------
# 🔹 Treina ou carrega o modelo
# -------------------------------
def train_or_load_model():
    if os.path.exists(MODEL_PATH):
        model = load(MODEL_PATH)
        return model
    df = pd.read_csv(CSV_PATH)
    colunas = ['n1','n2','n3','n4','n5','n6']
    if not all(col in df.columns for col in colunas):
        raise ValueError("CSV deve conter colunas n1..n6")
    X = np.arange(len(df)).reshape(-1,1)
    y = df[colunas].values
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X, y)
    dump(model, MODEL_PATH)
    return model

# -------------------------------
# 🔹 Endpoint /predict
# -------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    dia = data.get("dia")
    if dia is None:
        return jsonify({"error":"Informe o dia"}), 400

    # 1️⃣ Bola do dia
    combinacoes_geradas = gerar_combinacoes_pela_bola(dia)

    # 2️⃣ Previsão do ML
    try:
        model = train_or_load_model()
        y_pred = model.predict(np.array([[dia]]))
        previsao_modelo = y_pred[0].tolist()
    except Exception as e:
        print("Erro ML:", e)
        previsao_modelo = []

    # 3️⃣ Gerar 6 jogos combinando bola + ML
    jogos_sugeridos = []
    for i in range(6):
        jogo = sorted(list(set(
            combinacoes_geradas + previsao_modelo[i:i+1]
        )))[:6]
        jogos_sugeridos.append(jogo)

    return jsonify({
        "combinacoes_geradas": combinacoes_geradas,
        "previsao_modelo": previsao_modelo,
        "jogos_sugeridos": jogos_sugeridos,
        "dia": dia
    })

# -------------------------------
# 🔹 Rodar servidor
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
