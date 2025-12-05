from flask import Flask, request, jsonify
import numpy as np
import joblib
import matplotlib.pyplot as plt
import base64
import io
import random
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
CORS(app)

# Carrega ou treina modelo fictício
try:
    model = joblib.load("model_megasena.pkl")
except:
    X = np.random.randint(1, 61, (1000, 6))
    y = np.random.randint(0, 2, 1000)
    model = RandomForestClassifier()
    model.fit(X, y)
    joblib.dump(model, "model_megasena.pkl")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        dia = data.get("dia", 0)

        # Gerar combinação base (6 números)
        base = random.sample(range(1, 61), 6)
        X_input = np.array(base).reshape(1, -1)

        pred = model.predict(X_input)

        # Gerar 6 jogos
        jogos = []
        for _ in range(6):
            numeros = random.sample(range(1, 61), 6)
            numeros.sort()
            jogos.append(numeros)

        # Probabilidade de cada número (aleatória simulada)
        prob = np.random.rand(60)
        prob /= prob.sum()

        # Gera gráfico de distribuição
        plt.figure(figsize=(10, 4))
        plt.bar(range(1, 61), prob * 100)
        plt.title("Probabilidade de Saída dos Números (Teoria da Bola + ML)")
        plt.xlabel("Números (1–60)")
        plt.ylabel("Probabilidade (%)")
        plt.tight_layout()

        # Converter gráfico em Base64
        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        img_b64 = base64.b64encode(img.read()).decode('utf-8')
        plt.close()

        resposta = {
            "combinacoes_geradas": base,
            "dia": dia,
            "jogos_sugeridos": jogos,
            "previsao_modelo": pred.tolist(),
            "probabilidades": prob.tolist(),
            "grafico_base64": img_b64
        }

        return jsonify(resposta)

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
