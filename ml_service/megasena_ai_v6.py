from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

app = Flask(__name__)

MODEL_FILE = "megasena_rf_model.joblib"
CSV_FILE = "resultados_megasena.csv"

# ----------------------------
# Função para treinar o modelo
# ----------------------------
def treinar_modelo():
    if not os.path.exists(CSV_FILE):
        print("⚠️ Arquivo CSV não encontrado!")
        return None

    df = pd.read_csv(CSV_FILE)

    # Verifica colunas esperadas
    if not all(col in df.columns for col in ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']):
        print("❌ O CSV precisa conter colunas n1 até n6.")
        return None

    X = df[['n1', 'n2', 'n3', 'n4', 'n5', 'n6']].values
    y = np.arange(len(df)) % 2  # rótulo fictício apenas para treinar

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_FILE)
    print("✅ Modelo treinado e salvo em", MODEL_FILE)
    return model


# ----------------------------
# Função para carregar modelo
# ----------------------------
def carregar_modelo():
    if os.path.exists(MODEL_FILE):
        print("✅ Modelo carregado:", MODEL_FILE)
        return joblib.load(MODEL_FILE)
    else:
        print("⚙️ Treinando modelo inicial...")
        return treinar_modelo()


# ----------------------------
# Função da Teoria da Bola
# ----------------------------
def teoria_da_bola(dia):
    # Padrão antigo (mantido para fallback)
    base = dia % 10
    cadeia_mais4 = [(base + i * 4) % 60 + 1 for i in range(6)]
    cadeia_mais3 = [(base + i * 3) % 60 + 1 for i in range(6)]
    combinacao = sorted(list(set(cadeia_mais4[:3] + cadeia_mais3[:3])))

    # --- NOVO: usar padrões históricos ---
    try:
        df = pd.read_csv(CSV_FILE)
        bolas = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
        # Frequência absoluta
        todas_bolas = pd.concat([df[b] for b in bolas])
        freq = todas_bolas.value_counts().sort_index()
        # Atraso (quantos concursos sem sair)
        atraso = {n: 0 for n in range(1, 61)}
        for n in range(1, 61):
            ult = (df[bolas] == n).any(axis=1)[::-1].idxmax()
            atraso[n] = len(df) - ult
        # Último sorteio
        ultimos = df.iloc[-1][bolas].values.tolist()
        penultimos = df.iloc[-2][bolas].values.tolist() if len(df) > 1 else ultimos
        # Números que mais repetem de um sorteio para o outro
        repetidos = list(set(ultimos) & set(penultimos))
        # Números mais frequentes
        top_freq = freq.sort_values(ascending=False).head(10).index.tolist()
        # Números mais atrasados
        top_atraso = sorted(atraso, key=atraso.get, reverse=True)[:10]
        # Mistura: dia, frequentes, atrasados, repetidos
        candidatos = list(set([dia, base] + top_freq[:4] + top_atraso[:2] + repetidos))
        # Garante 6 números únicos
        while len(candidatos) < 6:
            candidatos.append(np.random.randint(1, 61))
        combinacao = sorted(list(set(candidatos))[:6])
    except Exception as e:
        print('Erro ao usar padrões históricos:', e)
        # fallback para padrão antigo
        pass
    return sorted(combinacao)


# ----------------------------
# Gera probabilidades simples
# ----------------------------
def calcular_probabilidades():
    df = pd.read_csv(CSV_FILE)
    bolas = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
    todas_bolas = pd.concat([df[b] for b in bolas])
    freq = todas_bolas.value_counts().sort_index()
    total = freq.sum()
    prob = (freq / total * 100).round(2)
    top_bolas = prob.sort_values(ascending=False).head(6)
    return {
        "mais_frequentes": top_bolas.to_dict(),
        "media_ocorrencias": round(freq.mean(), 2)
    }


# ----------------------------
# Rota principal de previsão
# ----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    dia = int(data.get("dia", 1))

    combinacao_teoria = teoria_da_bola(dia)

    model = carregar_modelo()
    if model is None:
        return jsonify({"erro": "Falha ao carregar modelo"}), 500

    # Previsão do modelo (apenas para referência)
    X_pred = np.array([combinacao_teoria])
    try:
        pred = model.predict(X_pred)
    except Exception as e:
        print("Erro ML:", e)
        pred = []

    # Geração de 6 jogos inteligentes:
    # 1. Baseado em padrões históricos (freq, atraso, repetição)
    # 2. Pequenas variações para cada jogo
    jogos = []
    for i in range(6):
        # Variação: soma do dia, frequência e atraso
        try:
            df = pd.read_csv(CSV_FILE)
            bolas = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
            todas_bolas = pd.concat([df[b] for b in bolas])
            freq = todas_bolas.value_counts().sort_index()
            atraso = {n: 0 for n in range(1, 61)}
            for n in range(1, 61):
                ult = (df[bolas] == n).any(axis=1)[::-1].idxmax()
                atraso[n] = len(df) - ult
            top_freq = freq.sort_values(ascending=False).head(10).index.tolist()
            top_atraso = sorted(atraso, key=atraso.get, reverse=True)[:10]
            ultimos = df.iloc[-1][bolas].values.tolist()
            penultimos = df.iloc[-2][bolas].values.tolist() if len(df) > 1 else ultimos
            repetidos = list(set(ultimos) & set(penultimos))
            base_jogo = list(set([dia, (dia+i)%60+1] + top_freq[:3] + top_atraso[:2] + repetidos))
            while len(base_jogo) < 6:
                base_jogo.append(np.random.randint(1, 61))
            jogo = sorted(list(set(base_jogo))[:6])
        except Exception as e:
            print('Erro ao gerar jogo inteligente:', e)
            # fallback: variação simples
            jogo = [(n + i * 2) % 60 + 1 for n in combinacao_teoria]
            jogo = sorted(list(set(jogo))[:6])
        jogos.append(jogo)

    probabilidades = calcular_probabilidades()

    return jsonify({
        "dia": dia,
        "combinacao_teoria": combinacao_teoria,
        "jogos_sugeridos": jogos,
        "probabilidades": probabilidades,
        "previsao_modelo": pred.tolist() if len(pred) > 0 else []
    })


# ----------------------------
# Inicialização
# ----------------------------
if __name__ == "__main__":
    carregar_modelo()
    print("🚀 Servidor Flask rodando em http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
