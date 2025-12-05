from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import os

# ----------------------------------------------------------
# 🔹 Configurações principais
# ----------------------------------------------------------
MODEL_PATH = "megasena_rf_model.joblib"
CSV_PATH = "resultados_megasena.csv"
app = Flask(__name__)

# ----------------------------------------------------------
# 🔹 Função para gerar combinações usando a regra da "bola do dia"
# ----------------------------------------------------------
def gerar_combinacoes_pela_bola(dia_base: int):
    """
    Base = último dígito do dia
    Cria duas cadeias: +4 e +3, depois faz concatenações cumulativas
    """
    base = dia_base % 10
    # Cadeia +4
    cadeia_4 = [(base + 4*i) % 60 for i in range(1, 7)]
    # Cadeia +3
    cadeia_3 = [(base + 3*i) % 60 for i in range(1, 7)]
    # Combinação cumulativa para formar dezenas plausíveis
    combinacoes = []
    for a, b in zip(cadeia_4, cadeia_3):
        combinacoes.append(a if a != 0 else 60)
        combinacoes.append(b if b != 0 else 60)
    # Seleciona 6 números únicos ordenados
    combinacoes_unicas = sorted(list(set(combinacoes)))[:6]
    return combinacoes_unicas

# ----------------------------------------------------------
# 🔹 Função para treinar ou carregar modelo
# ----------------------------------------------------------
def train_or_load_model():
    if os.path.exists(MODEL_PATH):
        print("✅ Carregando modelo existente...")
        model = load(MODEL_PATH)
        return model
    else:
        print("🧠 Treinando novo modelo...")
        df = pd.read_csv(CSV_PATH)
        # Garantir que temos colunas n1..n6
        colunas_dezenas = ['n1','n2','n3','n4','n5','n6']
        if not all(col in df.columns for col in colunas_dezenas):
            raise ValueError("❌ CSV deve conter colunas n1..n6")
        X = df.index.values.reshape(-1,1)  # Usa índice como feature simples
        y = df[colunas_dezenas].values
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(X, y)
        dump(model, MODEL_PATH)
        print("✅ Modelo treinado e salvo!")
        return model

# ----------------------------------------------------------
# 🔹 Endpoint para previsão
# ----------------------------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    dia = data.get("dia")
    if dia is None:
        return jsonify({"error":"Informe o dia"}), 400

    # 1️⃣ Gera números pela regra da bola
    combinacoes_geradas = gerar_combinacoes_pela_bola(dia)

    # 2️⃣ Previsão do modelo ML
    try:
        model = train_or_load_model()
        # Para simplificação, usamos índice = dia
        X_pred = np.array([[dia]])
        y_pred = model.predict(X_pred)
        previsao_modelo = y_pred[0].tolist()
    except Exception as e:
        print("⚠️ Erro ao prever:", e)
        previsao_modelo = None

    # 3️⃣ Combina os dois métodos para gerar 6 jogos
    jogos_sugeridos = []
    for i in range(6):
        jogo = sorted(list(set(
            combinacoes_geradas + (previsao_modelo[i:i+1] if previsao_modelo else [])
        )))[:6]
        jogos_sugeridos.append(jogo)

    return jsonify({
        "combinacoes_geradas": combinacoes_geradas,
        "previsao_modelo": previsao_modelo,
        "jogos_sugeridos": jogos_sugeridos,
        "dia": dia
    })

# ----------------------------------------------------------
# 🔹 Inicializa o servidor
# ----------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
