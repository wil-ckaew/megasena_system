from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import os
import random

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
        val = (base + i*4 + i*3) % 60
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
# 🔹 Gera 6 jogos distintos
# -------------------------------
def gerar_jogos(combinacoes_base, previsao_ml):
    jogos = []
    for _ in range(6):
        jogo = combinacoes_base.copy()
        # adicionar 0 a 2 números do ML se houver previsão
        if previsao_ml:
            for n in random.sample(previsao_ml, min(2,len(previsao_ml))):
                if n not in jogo:
                    jogo[random.randint(0,5)] = n
        # pequenas permutações aleatórias
        random.shuffle(jogo)
        jogos.append(sorted(list(set(jogo)))[:6])
    return jogos

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
    previsao_modelo = []
    try:
        model = train_or_load_model()
        y_pred = model.predict(np.array([[dia]]))
        previsao_modelo = y_pred[0].tolist()
    except Exception as e:
        print("Erro ML:", e)

    # 3️⃣ Gerar 6 jogos combinando bola + ML
    jogos_sugeridos = gerar_jogos(combinacoes_geradas, previsao_modelo)

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
