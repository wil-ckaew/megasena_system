from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import os
import random

# ----------------------------------------------------------
# Configurações principais
# ----------------------------------------------------------
MODEL_PATH = "megasena_rf_model.joblib"
CSV_PATH = "resultados_megasena.csv"

app = Flask(__name__)

# ----------------------------------------------------------
# Função para gerar combinações pelo cálculo da "bola do dia"
# ----------------------------------------------------------
def gerar_combinacoes_pela_bola(dia_base: int):
    base = dia_base % 10
    # cadeias +4 e +3
    cadeia_4 = [(base + 4*i) % 10 for i in range(8)]
    cadeia_3 = [(base + 3*i) % 10 for i in range(8)]

    # gera números candidatos
    candidatos = set()
    # concatena dígitos consecutivos das cadeias
    for i in range(len(cadeia_4)-1):
        n = int(f"{cadeia_4[i]}{cadeia_4[i+1]}")
        if 1 <= n <= 60:
            candidatos.add(n)
    for i in range(len(cadeia_3)-1):
        n = int(f"{cadeia_3[i]}{cadeia_3[i+1]}")
        if 1 <= n <= 60:
            candidatos.add(n)
    
    # soma cumulativa das cadeias
    soma = 0
    for n in cadeia_4 + cadeia_3:
        soma += n
        if 1 <= soma <= 60:
            candidatos.add(soma)
    
    # garante 6 números únicos
    numeros = sorted(list(candidatos))
    while len(numeros) < 6:
        n = random.randint(1,60)
        if n not in numeros:
            numeros.append(n)
    return sorted(numeros[:6])

# ----------------------------------------------------------
# Função para treinar modelo de ML
# ----------------------------------------------------------
def train_model():
    if not os.path.exists(CSV_PATH):
        print(f"CSV não encontrado: {CSV_PATH}")
        return None
    
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]

    dezenas_cols = [c for c in df.columns if c.startswith("n")]
    if not dezenas_cols:
        raise ValueError("Nenhuma coluna de dezenas encontrada no CSV.")
    
    X = []
    y = []
    
    for _, row in df.iterrows():
        try:
            day = int(row["data"].split("/")[0])
        except:
            day = 1
        
        features = [day % 10]
        X.append(features)
        y.append(int(row[dezenas_cols[0]]))  # target simplificado
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    dump(clf, MODEL_PATH)
    print("Modelo treinado e salvo em", MODEL_PATH)
    return clf

# ----------------------------------------------------------
# Carrega modelo
# ----------------------------------------------------------
def load_model():
    if os.path.exists(MODEL_PATH):
        return load(MODEL_PATH)
    else:
        return train_model()

model = load_model()

# ----------------------------------------------------------
# Endpoint de previsão
# ----------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    dia = data.get("dia", 1)
    
    combinacoes = gerar_combinacoes_pela_bola(dia)
    
    try:
        previsao_modelo = int(model.predict([[dia % 10]])[0])
    except:
        previsao_modelo = None
    
    return jsonify({
        "dia": dia,
        "previsao_modelo": previsao_modelo,
        "combinacoes_geradas": combinacoes
    })

# ----------------------------------------------------------
# Inicializa serviço
# ----------------------------------------------------------
if __name__ == "__main__":
    print("ML Service rodando em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)
