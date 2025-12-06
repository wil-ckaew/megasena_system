#!/usr/bin/env python3
"""
IA Python REAL para Mega-Sena - Analisa dados históricos do CSV
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import random
from collections import Counter
import sys
import os

app = Flask(__name__)
CORS(app)

print("🤖 INICIANDO IA PYTHON PARA MEGA-SENA")
print("="*60)

# Carregar dados históricos
CSV_PATH = 'resultados_megasena.csv'
try:
    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV carregado: {len(df)} sorteios históricos")
    print(f"📊 Período: {df['Data'].iloc[-1]} a {df['Data'].iloc[0]}")
    
    # Preparar análise
    all_games = []
    for _, row in df.iterrows():
        game = [int(row['n1']), int(row['n2']), int(row['n3']), 
                int(row['n4']), int(row['n5']), int(row['n6'])]
        all_games.append(sorted(game))
    
    # Análise estatística
    all_numbers = [num for game in all_games for num in game]
    freq = Counter(all_numbers)
    
    print(f"📈 Número mais frequente: {freq.most_common(1)[0]}")
    print(f"🔢 Total de números analisados: {len(all_numbers)}")
    
except Exception as e:
    print(f"❌ Erro ao carregar CSV: {e}")
    print("⚠️  Usando dados de exemplo...")
    df = None
    all_games = []

class MegaSenaAI:
    def __init__(self, historical_games):
        self.games = historical_games
        self.analyze_data()
    
    def analyze_data(self):
        """Analisa todos os dados históricos"""
        if not self.games:
            return
        
        # 1. Frequência geral
        all_nums = [num for game in self.games for num in game]
        self.freq = Counter(all_nums)
        
        # 2. Números quentes (últimos 20% dos sorteios)
        hot_cutoff = int(len(self.games) * 0.2)
        hot_games = self.games[-hot_cutoff:] if hot_cutoff > 0 else self.games
        hot_nums = [num for game in hot_games for num in game]
        self.hot_freq = Counter(hot_nums)
        
        # 3. Análise por posição
        self.position_stats = {}
        for pos in range(6):
            pos_nums = [game[pos] for game in self.games if len(game) > pos]
            if pos_nums:
                self.position_stats[pos] = {
                    'min': min(pos_nums),
                    'max': max(pos_nums),
                    'avg': np.mean(pos_nums),
                    'common': Counter(pos_nums).most_common(5)
                }
        
        # 4. Padrões de soma
        self.sums = [sum(game) for game in self.games]
        self.avg_sum = np.mean(self.sums) if self.sums else 210
        
        print(f"📊 IA treinada com {len(self.games)} jogos")
        print(f"💰 Soma média histórica: {self.avg_sum:.1f}")
    
    def generate_smart_numbers(self, day):
        """Gera números inteligentes baseados nos dados históricos"""
        
        if not self.games or len(self.games) < 10:
            # Fallback se não tiver dados
            return self.generate_random_numbers()
        
        # Usar dia como semente para reprodutibilidade
        seed = day + hash(str(self.games[-1])) if self.games else day
        random.seed(seed)
        
        selected = set()
        
        # ESTRATÉGIA 1: Números frequentes (40% de chance)
        if random.random() < 0.4:
            common_nums = [num for num, _ in self.freq.most_common(15)]
            if common_nums:
                selected.add(random.choice(common_nums))
        
        # ESTRATÉGIA 2: Números quentes (30% de chance)
        if random.random() < 0.3 and hasattr(self, 'hot_freq'):
            hot_nums = [num for num, _ in self.hot_freq.most_common(10)]
            if hot_nums:
                selected.add(random.choice(hot_nums))
        
        # ESTRATÉGIA 3: Considerar posições históricas
        for pos in range(6):
            if pos in self.position_stats:
                common_at_pos = [num for num, _ in self.position_stats[pos]['common']]
                if common_at_pos and random.random() < 0.5:
                    selected.add(random.choice(common_at_pos))
        
        # ESTRATÉGIA 4: Garantir números altos (≥35) baseado na média histórica
        high_ratio = sum(1 for game in self.games for num in game if num >= 35) / max(1, len(self.games) * 6)
        target_highs = max(1, int(high_ratio * 6))
        
        current_highs = sum(1 for num in selected if num >= 35)
        while current_highs < target_highs and len(selected) < 6:
            new_high = random.randint(35, 60)
            selected.add(new_high)
            current_highs += 1
        
        # ESTRATÉGIA 5: Completar até 6 números
        while len(selected) < 6:
            # Balancear entre frequentes e atrasados
            all_possible = list(range(1, 61))
            
            # Remover já selecionados
            possible = [n for n in all_possible if n not in selected]
            
            if not possible:
                break
            
            # Escolher com bias para menos frequentes (evitar viés)
            weights = []
            for num in possible:
                freq_score = self.freq.get(num, 0)
                # Inverter: dar mais chance a números menos frequentes
                weight = 1.0 / (freq_score + 1)
                weights.append(weight)
            
            # Normalizar pesos
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w/total_weight for w in weights]
                new_num = random.choices(possible, weights=weights, k=1)[0]
            else:
                new_num = random.choice(possible)
            
            selected.add(new_num)
        
        result = sorted(list(selected))
        
        # Ajustar soma se muito diferente da média
        current_sum = sum(result)
        if abs(current_sum - self.avg_sum) > 50:
            result = self.adjust_sum(result, self.avg_sum)
        
        return result
    
    def generate_random_numbers(self):
        """Fallback: gera números aleatórios"""
        numbers = set()
        while len(numbers) < 6:
            numbers.add(random.randint(1, 60))
        return sorted(list(numbers))
    
    def adjust_sum(self, numbers, target_sum):
        """Ajusta soma trocando números"""
        result = numbers.copy()
        current_sum = sum(result)
        
        attempts = 0
        while abs(current_sum - target_sum) > 30 and attempts < 20:
            idx = random.randint(0, 5)
            old_num = result[idx]
            
            if current_sum > target_sum:
                # Trocar por número menor
                candidates = [n for n in range(1, old_num) if n not in result]
            else:
                # Trocar por número maior
                candidates = [n for n in range(old_num + 1, 61) if n not in result]
            
            if candidates:
                result[idx] = random.choice(candidates)
                result.sort()
                current_sum = sum(result)
            
            attempts += 1
        
        return result

# Inicializar IA
ai = MegaSenaAI(all_games)

@app.route('/')
def home():
    return jsonify({
        'service': 'Mega-Sena Python IA',
        'version': '1.0',
        'status': 'online',
        'sorteios_analisados': len(all_games),
        'algoritmo': 'Análise estatística + IA',
        'endpoints': ['/health', '/api/generate']
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Mega-Sena Python IA',
        'timestamp': datetime.now().isoformat(),
        'sorteios_analisados': len(all_games),
        'ia_treinada': len(all_games) >= 10
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        day = data.get('day', datetime.now().day)
        
        print(f"🧠 IA Python processando dia {day}...")
        
        # Gerar números com IA
        numbers = ai.generate_smart_numbers(day)
        
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
            'method': 'python_ai_statistical',
            'service': 'python_ia',
            'sorteios_usados': len(all_games),
            'note': f'Gerado por IA Python analisando {len(all_games)} sorteios históricos'
        }
        
        print(f"✅ Números gerados pela IA: {numbers}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("="*60)
    print("🌐 Serviço IA Python iniciando na porta 5000")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
