from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import random
import sys
import os

app = Flask(__name__)
CORS(app)

# Carregar dados históricos
print("📊 Carregando dados históricos da Mega-Sena...")
try:
    df = pd.read_csv('resultados_megasena.csv')
    print(f"✅ {len(df)} sorteios carregados")
    
    # Analisar padrões
    all_numbers = []
    for _, row in df.iterrows():
        game = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
        all_numbers.extend(game)
    
    from collections import Counter
    freq = Counter(all_numbers)
    print(f"📈 Número mais frequente: {freq.most_common(1)[0]}")
    
except Exception as e:
    print(f"⚠️  Erro ao carregar CSV: {e}")
    df = None

def generate_smart_numbers(day):
    """Gera números usando análise estatística dos dados históricos"""
    
    if df is None or len(df) < 10:
        # Fallback: random se não tiver dados
        return sorted(random.sample(range(1, 61), 6))
    
    # 1. Análise de frequência
    freq_numbers = []
    for col in ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']:
        if col in df.columns:
            col_data = df[col].dropna().astype(int)
            if len(col_data) > 0:
                # Pegar números mais comuns nesta posição
                common = col_data.value_counts().head(3).index.tolist()
                freq_numbers.extend(common)
    
    # 2. Números quentes (últimos 10 sorteios)
    hot_numbers = []
    if len(df) >= 10:
        last_10 = df.tail(10)
        for _, row in last_10.iterrows():
            game = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
            hot_numbers.extend(game)
    
    from collections import Counter
    hot_counter = Counter(hot_numbers)
    
    # 3. Combinar análise
    candidates = set()
    
    # Adicionar números frequentes
    for num in freq_numbers[:10]:
        candidates.add(num)
    
    # Adicionar números quentes
    for num, _ in hot_counter.most_common(10):
        candidates.add(num)
    
    # 4. Usar dia como fator de variação
    day_factor = day % 31
    base_numbers = list(candidates)
    
    # Selecionar 6 números
    selected = []
    if len(base_numbers) >= 6:
        # Ordenar por "pontuação"
        scores = []
        for num in base_numbers:
            score = 0
            # Pontuar por frequência
            if num in freq_numbers:
                score += 2
            # Pontuar por ser quente
            if hot_counter.get(num, 0) > 1:
                score += 3
            # Adicionar fator do dia
            if (num + day_factor) % 7 == 0:
                score += 1
            scores.append((num, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        selected = [num for num, _ in scores[:6]]
    else:
        # Completar com números aleatórios
        selected = list(base_numbers)
        while len(selected) < 6:
            num = random.randint(1, 60)
            if num not in selected:
                selected.append(num)
    
    selected.sort()
    return selected

@app.route('/')
def home():
    return jsonify({
        'service': 'Mega-Sena Python ML',
        'version': '1.0',
        'status': 'online',
        'data_points': len(df) if df is not None else 0,
        'endpoints': ['/health', '/api/generate']
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Mega-Sena Python ML',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': df is not None,
        'sorteios_analisados': len(df) if df is not None else 0
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        day = data.get('day', datetime.now().day)
        
        print(f"🤖 Python ML gerando para dia {day}...")
        
        # Gerar números com IA
        numbers = generate_smart_numbers(day)
        
        response = {
            'success': True,
            'games': [{
                'numbers': numbers,
                'sum': sum(numbers),
                'high_numbers': sum(1 for n in numbers if n >= 35),
                'even_numbers': sum(1 for n in numbers if n % 2 == 0),
            }],
            'day': day,
            'timestamp': datetime.now().isoformat(),
            'method': 'python_ml_statistical',
            'service': 'python_ml',
            'data_used': len(df) if df is not None else 0,
            'note': 'Gerado com análise estatística de dados históricos'
        }
        
        print(f"✅ Números gerados: {numbers}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 MEGA-SENA PYTHON ML SERVICE")
    print("="*60)
    print(f"📊 Dados: resultados_megasena.csv")
    print(f"🌐 Porta: 5000")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
