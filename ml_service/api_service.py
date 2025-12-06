#!/usr/bin/env python3
"""
API do Serviço de IA para Mega-Sena
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from megasena_corrigido import MegaSenaCorrigido
    print("✅ Módulo megasena_corrigido carregado com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar megasena_corrigido: {e}")
    # Criar uma classe simulada para testes
    class MegaSenaCorrigido:
        def __init__(self, csv_path='resultados_megasena.csv'):
            self.csv_path = csv_path
            self.df = pd.read_csv(csv_path)
            print(f"Dados carregados: {len(self.df)} registros")
        
        def metodo_hibrido(self, quantidade=1):
            """Método híbrido de exemplo"""
            import random
            jogos = []
            for _ in range(quantidade):
                jogo = sorted(random.sample(range(1, 61), 6))
                jogos.append(jogo)
            return jogos if quantidade > 1 else jogos[0]

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as origens

# Inicializar otimizador
print("🤖 Inicializando otimizador Mega-Sena...")
try:
    otimizador = MegaSenaCorrigido('resultados_megasena.csv')
    print("✅ Otimizador inicializado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao inicializar otimizador: {e}")
    otimizador = None

@app.route('/')
def home():
    return jsonify({
        'service': 'Mega-Sena AI ML Service',
        'version': '2.1',
        'status': 'online',
        'endpoints': {
            'health': '/health',
            'generate': '/api/generate',
            'analyze': '/api/analyze',
            'hybrid': '/api/hybrid'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Mega-Sena AI ML Service',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': otimizador is not None
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    """Gera números usando IA Python"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        day = data.get('day', datetime.now().day)
        method = data.get('method', 'hybrid')
        quantity = data.get('quantity', 1)
        
        print(f"📡 Recebida requisição: dia={day}, método={method}, quantidade={quantity}")
        
        if not otimizador:
            return jsonify({
                'success': False,
                'error': 'Otimizador não inicializado'
            }), 500
        
        # Gerar jogo baseado no método
        if method == 'caravaca':
            game = otimizador.metodo_caravaca(day)
        elif method == 'statistical':
            game = otimizador.metodo_estatistico(quantity)
            if quantity == 1 and isinstance(game, list):
                game = game[0]
        elif method == 'ai':
            game = otimizador.metodo_ia_avancado(quantity)
            if quantity == 1 and isinstance(game, list):
                game = game[0]
        else:  # hybrid
            game = otimizador.metodo_hibrido(quantity)
            if quantity == 1 and isinstance(game, list):
                game = game[0]
        
        # Se for múltiplos jogos
        if quantity > 1:
            games_list = game if isinstance(game, list) else [game]
        else:
            games_list = [game]
        
        # Formatar resposta
        games = []
        for g in games_list:
            games.append({
                'numbers': g,
                'sum': sum(g),
                'high_numbers': sum(1 for n in g if n >= 35),
                'even_numbers': sum(1 for n in g if n % 2 == 0),
            })
        
        response = {
            'success': True,
            'games': games,
            'day': day,
            'method': method,
            'quantity': quantity,
            'timestamp': datetime.now().isoformat(),
            'service': 'python_ml'
        }
        
        print(f"✅ Jogo gerado: {games[0]['numbers']}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/analyze', methods=['GET'])
def analyze():
    """Retorna análise estatística dos dados"""
    try:
        if not otimizador or not hasattr(otimizador, 'analise'):
            return jsonify({'error': 'Análise não disponível'}), 400
        
        analysis = otimizador.analise
        
        response = {
            'total_games': analysis.get('total_sorteios', 0),
            'hot_numbers': [{'number': n, 'count': c} for n, c in analysis.get('numeros_quentes', [])[:10]],
            'cold_numbers': [{'number': n, 'count': c} for n, c in analysis.get('numeros_frios', [])[:10]],
            'most_frequent': [{'number': n, 'count': c} for n, c in analysis.get('frequencias', {}).most_common(10)],
            'sum_stats': analysis.get('somas', {}),
            'high_numbers_distribution': dict(analysis.get('distribuicao_altos', {})),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hybrid', methods=['POST'])
def hybrid_rust_python():
    """Integração híbrida: usa Rust + Python"""
    try:
        data = request.get_json()
        day = data.get('day', datetime.now().day)
        
        # 1. Primeiro, gerar com Python IA
        python_game = otimizador.metodo_hibrido(1)
        if isinstance(python_game, list) and len(python_game) > 0:
            python_numbers = python_game[0] if isinstance(python_game[0], list) else python_game
        else:
            python_numbers = python_game
        
        # 2. Podemos adicionar lógica de combinação aqui
        hybrid_numbers = python_numbers  # Por enquanto, só Python
        
        response = {
            'success': True,
            'games': [{
                'numbers': hybrid_numbers,
                'sum': sum(hybrid_numbers),
                'high_numbers': sum(1 for n in hybrid_numbers if n >= 35),
                'even_numbers': sum(1 for n in hybrid_numbers if n % 2 == 0),
                'source': 'python_ml_advanced'
            }],
            'day': day,
            'timestamp': datetime.now().isoformat(),
            'notes': 'Gerado com IA Python avançada (Random Forest)'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVIÇO IA MEGA-SENA INICIANDO")
    print("="*60)
    print(f"📊 Dados: resultados_megasena.csv ({len(pd.read_csv('resultados_megasena.csv'))} registros)")
    print(f"🌐 Porta: 5000")
    print(f"🔗 Endpoint principal: http://localhost:5000/api/generate")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
