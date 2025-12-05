
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
import joblib
import os

app = Flask(__name__)
CORS(app)

# Caminhos
DATA_PATH = "resultados_megasena.csv"
MODEL_PATH = "megasena_rf_model.joblib"

# Garante que os dados existam
if not os.path.exists(DATA_PATH):
    df = pd.DataFrame(columns=[f"dezena_{i}" for i in range(1, 7)])
    df.to_csv(DATA_PATH, index=False)

# Carrega ou treina modelo simples
def carregar_modelo():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        df = pd.read_csv(DATA_PATH)
        if df.empty:
            return None

        X = df[[f"dezena_{i}" for i in range(1, 6)]]
        y = df["dezena_6"]
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(X, y)
        joblib.dump(model, MODEL_PATH)
        return model

modelo = carregar_modelo()

@app.route("/predict", methods=["POST"])
def predict():
    try:
        dados = request.get_json()
        dia = int(dados.get("dia", 0))

        if dia <= 0:
            return jsonify({"erro": "Dia inválido!"}), 400

        # Gera combinações aleatórias (simulação)
        combinacao_base = sorted(random.sample(range(1, 61), 6))
        jogos_sugeridos = [
            sorted(random.sample(range(1, 61), 6)) for _ in range(6)
        ]

        # Simula probabilidades
        probabilidades = [{"numero": i, "chance": round(random.uniform(0, 5), 2)} for i in range(1, 61)]

        # Simulação de previsão (se modelo treinado)
        previsao_modelo = []
        if modelo:
            X_pred = np.array(combinacao_base[:-1]).reshape(1, -1)
            pred = modelo.predict(X_pred)
            previsao_modelo = pred.tolist()

        return jsonify({
            "dia": dia,
            "combinacoes_geradas": combinacao_base,
            "jogos_sugeridos": jogos_sugeridos,
            "previsao_modelo": previsao_modelo,
            "probabilidades": probabilidades
        })

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
