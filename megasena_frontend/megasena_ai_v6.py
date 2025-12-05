from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # 🔥 Permite conexão do frontend React

# ---------------------------------------------
# Função simulada de carregamento de resultados
# ---------------------------------------------
def carregar_resultados(csv_path="resultados_megasena.csv"):
    if not os.path.exists(csv_path):
        data = {
            "concurso": list(range(1, 101)),
            "bola1": np.random.randint(1, 60, 100),
            "bola2": np.random.randint(1, 60, 100),
            "bola3": np.random.randint(1, 60, 100),
            "bola4": np.random.randint(1, 60, 100),
            "bola5": np.random.randint(1, 60, 100),
            "bola6": np.random.randint(1, 60, 100),
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
    return pd.read_csv(csv_path)

# ---------------------------------------------
# Função IA — gera previsões e probabilidades
# ---------------------------------------------
def gerar_previsao(dia):
    df = carregar_resultados()
    X = np.array(df["concurso"]).reshape(-1, 1)
    y = df[["bola1", "bola2", "bola3", "bola4", "bola5", "bola6"]]

    model = LinearRegression()
    model.fit(X, y)

    previsao = model.predict([[dia]])[0]
    previsao = np.clip(previsao.round().astype(int), 1, 60)
    previsao = sorted(list(set(previsao)))

    # 🔢 Gerar 6 jogos baseados no modelo e aleatoriedade
    jogos_sugeridos = []
    for _ in range(6):
        base = list(previsao)
        while len(base) < 6:
            n = random.randint(1, 60)
            if n not in base:
                base.append(n)
        jogos_sugeridos.append(sorted(base))

    # 🔢 Calcular probabilidades simuladas
    todas_bolas = df[["bola1", "bola2", "bola3", "bola4", "bola5", "bola6"]].values.flatten()
    unique, counts = np.unique(todas_bolas, return_counts=True)
    freq = dict(zip(unique, counts))
    prob = {n: round((freq.get(n, 0) / len(todas_bolas)) * 100, 2) for n in range(1, 61)}

    return {
        "dia": dia,
        "combinacoes_geradas": previsao,
        "jogos_sugeridos": jogos_sugeridos,
        "probabilidades": prob
    }

# ---------------------------------------------
# Endpoint principal
# ---------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    dia = data.get("dia", 1)
    resultado = gerar_previsao(dia)
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
