#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA-SENA OTIMIZADOR - Versão corrigida
Autor: Wil Ckaew
Versão: 3.0
Data: Dez 2024
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
from collections import Counter, defaultdict
import warnings
import sys
import os
import statistics
from sklearn.linear_model import LinearRegression

warnings.filterwarnings('ignore')

class MegaSenaOtimizadorV3:
    def __init__(self, csv_path='resultados_megasena.csv'):
        """Inicializa o otimizador com dados históricos"""
        print("="*60)
        print("🎰 MEGA-SENA OTIMIZADOR - IA + ESTATÍSTICA + CARAVACA")
        print("="*60)
        
        print(f"📁 Usando arquivo: {csv_path}")
        
        try:
            # Tentar ler o CSV
            self.df = pd.read_csv(csv_path)
            print(f"✅ Dados carregados: {len(self.df)} sorteios históricos")
            
            # Verificar formato das colunas
            if 'n1' in self.df.columns:
                print("✅ Formato detectado: n1, n2, n3, n4, n5, n6")
                self.colunas_numeros = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
            elif 'bola 1' in self.df.columns:
                print("✅ Formato detectado: bola 1, bola 2, ...")
                self.colunas_numeros = ['bola 1', 'bola 2', 'bola 3', 'bola 4', 'bola 5', 'bola 6']
            else:
                # Tentar descobrir automaticamente
                num_cols = [col for col in self.df.columns if any(x in str(col).lower() for x in ['bola', 'n', 'num'])]
                if len(num_cols) >= 6:
                    self.colunas_numeros = num_cols[:6]
                    print(f"✅ Colunas detectadas automaticamente: {self.colunas_numeros}")
                else:
                    raise ValueError("Não foi possível identificar as colunas de números")
            
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            print("⚠️  Gerando dados de exemplo...")
            self.gerar_dados_exemplo()
        
        self.todos_numeros = list(range(1, 61))
        self.analise = {}
        self.preparar_dados()
    
    def gerar_dados_exemplo(self):
        """Gera dados de exemplo se CSV não existir ou tiver erro"""
        print("📊 Gerando dados de exemplo...")
        np.random.seed(42)
        dados = []
        for i in range(100):
            # Garantir que tenha números altos (35-60)
            nums = []
            # 1-2 números altos por jogo (mais realista)
            num_altos = random.randint(1, 3)
            altos = random.sample(range(35, 61), num_altos)
            baixos_medios = random.sample(range(1, 35), 6 - num_altos)
            nums = sorted(altos + baixos_medios)
            
            dados.append({
                'Concurso': 3000 - i,
                'Data': f'2023-{(i%12)+1:02d}-{(i%28)+1:02d}',
                'n1': nums[0],
                'n2': nums[1],
                'n3': nums[2],
                'n4': nums[3],
                'n5': nums[4],
                'n6': nums[5]
            })
        self.df = pd.DataFrame(dados)
        self.colunas_numeros = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
        
        # Salvar para referência
        self.df.to_csv('resultados_megasena_exemplo.csv', index=False)
        print("✅ Dados de exemplo gerados e salvos")
    
    def preparar_dados(self):
        """Prepara e analisa todos os dados históricos"""
        print("\n📊 Analisando dados históricos...")
        
        try:
            # Converter para inteiros
            for col in self.colunas_numeros:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').astype(int)
            
            # 1. Análise de Frequência
            frequencias = Counter()
            for col in self.colunas_numeros:
                frequencias.update(self.df[col].values)
            
            # Preencher números que nunca saíram com 0
            for num in self.todos_numeros:
                if num not in frequencias:
                    frequencias[num] = 0
            
            total_sorteios = len(self.df)
            
            # 2. Cálculo de Atrasos
            atrasos = {}
            for num in self.todos_numeros:
                # Encontrar última ocorrência
                mask = (self.df[self.colunas_numeros] == num).any(axis=1)
                if mask.any():
                    ultimo_idx = mask[mask].index.max()
                    atraso = total_sorteios - ultimo_idx
                else:
                    atraso = total_sorteios
                atrasos[num] = atraso
            
            # 3. Padrões por Posição
            padroes_posicao = {}
            for i, col in enumerate(self.colunas_numeros):
                valores = self.df[col].values
                if len(valores) > 0:
                    try:
                        moda = statistics.mode(valores)
                    except:
                        moda = np.median(valores)
                    
                    padroes_posicao[i] = {
                        'media': float(np.mean(valores)),
                        'mediana': float(np.median(valores)),
                        'std': float(np.std(valores)) if len(valores) > 1 else 0,
                        'min': int(np.min(valores)),
                        'max': int(np.max(valores)),
                        'moda': int(moda),
                        'comuns': Counter(valores).most_common(5)
                    }
                else:
                    padroes_posicao[i] = {
                        'media': 30.5, 'mediana': 30.5, 'std': 17.5,
                        'min': 1, 'max': 60, 'moda': 30,
                        'comuns': []
                    }
            
            # 4. Análise de Pares frequentes
            todos_jogos = []
            for _, row in self.df.iterrows():
                jogo = sorted([row[col] for col in self.colunas_numeros])
                todos_jogos.append(jogo)
            
            pares_frequentes = Counter()
            for jogo in todos_jogos:
                for i in range(len(jogo)):
                    for j in range(i+1, len(jogo)):
                        par = tuple(sorted([jogo[i], jogo[j]]))
                        pares_frequentes[par] += 1
            
            # 5. Distribuição de números altos (35-60)
            jogos_com_altos = []
            for jogo in todos_jogos:
                altos_no_jogo = sum(1 for num in jogo if num >= 35)
                jogos_com_altos.append(altos_no_jogo)
            
            distribuicao_altos = Counter(jogos_com_altos)
            
            # 6. Análise de Somas
            somas = [sum(jogo) for jogo in todos_jogos]
            
            self.analise = {
                'frequencias': frequencias,
                'atrasos': atrasos,
                'padroes_posicao': padroes_posicao,
                'pares_frequentes': pares_frequentes.most_common(20),
                'distribuicao_altos': distribuicao_altos,
                'somas': {
                    'media': float(np.mean(somas)) if somas else 180,
                    'std': float(np.std(somas)) if len(somas) > 1 else 50,
                    'min': int(np.min(somas)) if somas else 60,
                    'max': int(np.max(somas)) if somas else 360,
                },
                'todos_jogos': todos_jogos,
                'total_sorteios': total_sorteios,
                'colunas_usadas': self.colunas_numeros
            }
            
            print("✅ Análise concluída com sucesso!")
            
        except Exception as e:
            print(f"⚠️  Erro na análise: {e}")
            print("⚠️  Usando análise básica...")
            self.analise_basica()
    
    def analise_basica(self):
        """Análise básica em caso de erro"""
        self.analise = {
            'frequencias': Counter({i: 1 for i in range(1, 61)}),
            'atrasos': {i: 10 for i in range(1, 61)},
            'total_sorteios': 52,
            'somas': {'media': 180, 'std': 50, 'min': 60, 'max': 360},
            'distribuicao_altos': Counter({2: 30, 1: 15, 3: 7}),
            'todos_jogos': []
        }
    
    def metodo_caravaca(self, dia=None):
        """Implementa o método de Caravaca baseado no dia do mês"""
        if dia is None:
            dia = datetime.now().day
        
        # Fórmula adaptada de Caravaca
        numeros_base = []
        
        # Usar dia para gerar números
        for i in range(1, 7):
            # Fórmula principal ajustada
            num = (dia * i * 7) % 60
            if num == 0:
                num = 60
            
            # Ajustar distribuição
            if i >= 4:  # Últimas posições tendem a números mais altos
                num = min(60, num + random.randint(10, 25))
            
            numeros_base.append(num)
        
        # Garantir números únicos e válidos
        numeros_base = list(set([max(1, min(60, n)) for n in numeros_base]))
        
        while len(numeros_base) < 6:
            novo_num = random.randint(1, 60)
            if novo_num not in numeros_base:
                numeros_base.append(novo_num)
        
        # Ordenar e garantir que tenha números altos
        resultado = sorted(numeros_base[:6])
        
        # Garantir pelo menos 1 número alto (35-60)
        altos = sum(1 for n in resultado if n >= 35)
        if altos == 0:
            # Substituir o menor número por um alto
            resultado[0] = random.choice(range(35, 61))
            resultado.sort()
        
        return resultado
    
    def metodo_estatistico(self, quantidade=1):
        """Gera jogos baseados em estatísticas históricas"""
        jogos_gerados = []
        
        for _ in range(quantidade):
            # Usar pesos baseados em frequência e atraso
            pesos = []
            for num in self.todos_numeros:
                freq = self.analise['frequencias'].get(num, 1)
                atraso = self.analise['atrasos'].get(num, 10)
                
                # Fórmula: mais peso para números frequentes E atrasados
                peso_freq = freq / self.analise['total_sorteios']
                peso_atraso = min(1.0, atraso / 20)
                
                # Combinação: 40% frequência, 60% atraso (favorece números atrasados)
                peso = (0.4 * peso_freq) + (0.6 * peso_atraso)
                pesos.append(peso)
            
            # Normalizar pesos
            soma_pesos = sum(pesos)
            if soma_pesos > 0:
                pesos = [p/soma_pesos for p in pesos]
            else:
                pesos = [1/60] * 60
            
            # Escolher números
            numeros = []
            tentativas = 0
            while len(numeros) < 6 and tentativas < 100:
                num = np.random.choice(self.todos_numeros, p=pesos)
                if num not in numeros:
                    numeros.append(num)
                tentativas += 1
            
            # Se não conseguiu 6 números únicos, completar aleatoriamente
            while len(numeros) < 6:
                num = random.randint(1, 60)
                if num not in numeros:
                    numeros.append(num)
            
            resultado = sorted(numeros)
            
            # Ajustar para ter distribuição realista de números altos
            altos = sum(1 for n in resultado if n >= 35)
            
            # Estatística: geralmente 1-3 números altos por jogo
            if altos < 1:
                # Substituir um número baixo por alto
                baixos = [n for n in resultado if n < 35]
                if baixos:
                    resultado.remove(random.choice(baixos))
                    novo_alto = random.choice([n for n in range(35, 61) if n not in resultado])
                    resultado.append(novo_alto)
                    resultado.sort()
            elif altos > 4:
                # Muitos altos, substituir alguns
                while altos > 4:
                    altos_lista = [n for n in resultado if n >= 35]
                    if altos_lista:
                        resultado.remove(random.choice(altos_lista))
                        novo_medio = random.choice([n for n in range(20, 35) if n not in resultado])
                        resultado.append(novo_medio)
                        resultado.sort()
                    altos = sum(1 for n in resultado if n >= 35)
            
            jogos_gerados.append(resultado)
        
        return jogos_gerados if quantidade > 1 else jogos_gerados[0]
    
    def metodo_ia_simples(self, quantidade=1):
        """Método de IA simples baseado em padrões"""
        try:
            if len(self.df) < 10:
                raise ValueError("Dados insuficientes para IA")
            
            # Preparar features: últimos 5 jogos
            X = []
            y = []
            
            for i in range(5, len(self.df)):
                # Features: médias dos últimos 5 jogos
                features = []
                for j in range(5):
                    idx = i - 5 + j
                    jogo = [self.df.iloc[idx][col] for col in self.colunas_numeros]
                    features.extend([
                        np.mean(jogo),
                        np.std(jogo),
                        min(jogo),
                        max(jogo),
                        sum(1 for n in jogo if n >= 35)
                    ])
                
                # Target: próximo jogo
                target = [self.df.iloc[i][col] for col in self.colunas_numeros]
                
                X.append(features)
                y.append(target)
            
            if len(X) < 5:
                raise ValueError("Dados insuficientes para treino")
            
            X = np.array(X)
            y = np.array(y)
            
            jogos_gerados = []
            
            for _ in range(quantidade):
                # Usar últimos 5 jogos para prever
                ultimas_features = []
                for j in range(5):
                    idx = len(self.df) - 5 + j
                    if idx >= 0:
                        jogo = [self.df.iloc[idx][col] for col in self.colunas_numeros]
                    else:
                        jogo = [random.randint(1, 60) for _ in range(6)]
                    
                    ultimas_features.extend([
                        np.mean(jogo),
                        np.std(jogo),
                        min(jogo),
                        max(jogo),
                        sum(1 for n in jogo if n >= 35)
                    ])
                
                # Se não tem features suficientes, completar
                while len(ultimas_features) < 25:
                    ultimas_features.append(30.5)
                
                # Prever com modelo simples (média dos últimos)
                predicoes = []
                for pos in range(6):
                    # Média dos últimos valores nessa posição
                    ultimos_valores = []
                    for j in range(min(5, len(self.df))):
                        idx = len(self.df) - 1 - j
                        if idx >= 0:
                            ultimos_valores.append(self.df.iloc[idx][self.colunas_numeros[pos]])
                    
                    if ultimos_valores:
                        pred = np.mean(ultimos_valores) + random.uniform(-5, 5)
                    else:
                        pred = random.randint(1, 60)
                    
                    pred = int(np.clip(round(pred), 1, 60))
                    predicoes.append(pred)
                
                # Garantir números únicos
                predicoes = list(set(predicoes))
                while len(predicoes) < 6:
                    novo_num = random.randint(1, 60)
                    if novo_num not in predicoes:
                        predicoes.append(novo_num)
                
                resultado = sorted(predicoes[:6])
                
                # Ajustar números altos
                self.ajustar_numeros_altos(resultado)
                
                jogos_gerados.append(resultado)
            
            return jogos_gerados if quantidade > 1 else jogos_gerados[0]
            
        except Exception as e:
            print(f"⚠️  IA simples falhou: {e}, usando método estatístico")
            return self.metodo_estatistico(quantidade)
    
    def ajustar_numeros_altos(self, jogo):
        """Ajusta a quantidade de números altos no jogo"""
        altos = sum(1 for n in jogo if n >= 35)
        
        # Distribuição ideal: 1-3 números altos por jogo
        if altos < 1:
            # Adicionar um alto
            baixos = [n for n in jogo if n < 35]
            if baixos:
                jogo.remove(random.choice(baixos))
                novo_alto = random.choice([n for n in range(35, 61) if n not in jogo])
                jogo.append(novo_alto)
                jogo.sort()
        
        elif altos > 4:
            # Remover excesso de altos
            while altos > 3:
                altos_lista = [n for n in jogo if n >= 35]
                if altos_lista:
                    jogo.remove(random.choice(altos_lista))
                    novo_medio = random.choice([n for n in range(20, 35) if n not in jogo])
                    jogo.append(novo_medio)
                    jogo.sort()
                altos = sum(1 for n in jogo if n >= 35)
    
    def metodo_hibrido(self, quantidade=1):
        """Combina todos os métodos para melhor resultado"""
        jogos_gerados = []
        
        for _ in range(quantidade):
            # Gerar com diferentes métodos
            jogo1 = self.metodo_caravaca()
            jogo2 = self.metodo_estatistico()
            jogo3 = self.metodo_ia_simples()
            
            # Combinar e escolher os mais frequentes
            todos_numeros = jogo1 + jogo2 + jogo3
            contagem = Counter(todos_numeros)
            
            # Escolher os 6 números mais votados
            candidatos = [num for num, _ in contagem.most_common(12)]
            
            # Se houver empate, decidir por pesos
            pesos_finais = []
            for num in candidatos:
                peso_freq = self.analise['frequencias'].get(num, 0) / self.analise['total_sorteios']
                peso_atraso = min(1.0, self.analise['atrasos'].get(num, 0) / 15)
                peso_votos = contagem[num] / 3
                
                # Peso final: 30% frequência, 30% atraso, 40% votos
                peso_final = (0.3 * peso_freq) + (0.3 * peso_atraso) + (0.4 * peso_votos)
                pesos_finais.append((num, peso_final))
            
            # Ordenar por peso
            pesos_finais.sort(key=lambda x: x[1], reverse=True)
            
            # Pegar 6 melhores
            resultado = []
            for num, _ in pesos_finais[:6]:
                resultado.append(num)
            
            resultado.sort()
            
            # Ajuste final
            self.ajustar_numeros_altos(resultado)
            
            jogos_gerados.append(resultado)
        
        return jogos_gerados if quantidade > 1 else jogos_gerados[0]
    
    def gerar_relatorio(self):
        """Gera relatório completo da análise"""
        print("\n" + "="*60)
        print("📈 RELATÓRIO DE ANÁLISE MEGA-SENA")
        print("="*60)
        
        try:
            print(f"\n📊 Estatísticas Gerais:")
            print(f"   • Total de sorteios analisados: {self.analise.get('total_sorteios', 'N/A')}")
            print(f"   • Colunas usadas: {', '.join(self.colunas_numeros)}")
            
            print(f"\n🎯 Top 10 números mais frequentes:")
            if 'frequencias' in self.analise:
                for num, freq in self.analise['frequencias'].most_common(10):
                    perc = (freq / self.analise['total_sorteios']) * 100 if self.analise['total_sorteios'] > 0 else 0
                    print(f"   • {num:2d}: {freq:3d} vezes ({perc:.1f}%)")
            
            print(f"\n⏰ Top 10 números mais atrasados:")
            if 'atrasos' in self.analise:
                atrasos_ordenados = sorted(self.analise['atrasos'].items(), key=lambda x: x[1], reverse=True)
                for num, atraso in atrasos_ordenados[:10]:
                    print(f"   • {num:2d}: {atraso:3d} sorteios sem aparecer")
            
            print(f"\n🔢 Distribuição de números altos (35-60):")
            if 'distribuicao_altos' in self.analise:
                for qtd_altos, frequencia in sorted(self.analise['distribuicao_altos'].items()):
                    if self.analise['total_sorteios'] > 0:
                        perc = (frequencia / self.analise['total_sorteios']) * 100
                        print(f"   • {qtd_altos} número(s) alto(s): {frequencia:3d} vezes ({perc:.1f}%)")
            
            print(f"\n💰 Soma dos números por jogo:")
            if 'somas' in self.analise:
                print(f"   • Média: {self.analise['somas'].get('media', 0):.1f}")
                print(f"   • Mínima: {self.analise['somas'].get('min', 0)}")
                print(f"   • Máxima: {self.analise['somas'].get('max', 0)}")
            
            print(f"\n🤝 Top 5 pares mais frequentes:")
            if 'pares_frequentes' in self.analise:
                for par, freq in self.analise['pares_frequentes'][:5]:
                    print(f"   • {par[0]:2d} - {par[1]:2d}: {freq:3d} vezes")
                    
        except Exception as e:
            print(f"⚠️  Erro no relatório: {e}")

def main():
    """Função principal"""
    # Verificar se o arquivo CSV existe
    csv_file = 'resultados_megasena.csv'
    if not os.path.exists(csv_file):
        print(f"⚠️  Arquivo {csv_file} não encontrado!")
        print("📁 Procurando em subdiretórios...")
        for root, dirs, files in os.walk('.'):
            if 'resultados_megasena.csv' in files:
                csv_file = os.path.join(root, 'resultados_megasena.csv')
                print(f"✅ Encontrado em: {csv_file}")
                break
    
    # Inicializar otimizador
    otimizador = MegaSenaOtimizadorV3(csv_file)
    
    # Gerar relatório
    otimizador.gerar_relatorio()
    
    print("\n" + "="*60)
    print("🎲 JOGOS SUGERIDOS (OTIMIZADOS):")
    print("="*60)
    
    # Gerar jogos com diferentes métodos
    metodos = [
        ("1. Método Caravaca (dia do mês)", otimizador.metodo_caravaca),
        ("2. Método Estatístico", lambda: otimizador.metodo_estatistico(1)),
        ("3. Método IA Simples", lambda: otimizador.metodo_ia_simples(1)),
        ("4. Método Híbrido ⭐ RECOMENDADO", lambda: otimizador.metodo_hibrido(1)),
    ]
    
    for nome_metodo, metodo in metodos:
        try:
            jogo = metodo()
            soma = sum(jogo)
            altos = sum(1 for n in jogo if n >= 35)
            pares = sum(1 for n in jogo if n % 2 == 0)
            
            print(f"\n{nome_metodo}:")
            print(f"   Números: {', '.join(f'{n:2d}' for n in jogo)}")
            print(f"   Soma: {soma:3d} | Altos (≥35): {altos} | Pares: {pares}")
            
            # Verificar se tem números de 35 a 60
            if altos == 0:
                print(f"   ⚠️  ATENÇÃO: Nenhum número alto (35-60)!")
            
        except Exception as e:
            print(f"\n{nome_metodo}:")
            print(f"   ❌ Erro: {e}")
    
    print("\n" + "="*60)
    print("💡 DICAS PARA APOSTAS:")
    print("="*60)
    print("1. Misture números altos (35-60) e baixos (1-34)")
    print("2. Inclua números atrasados (veja relatório)")
    print("3. Use alguns números frequentes")
    print("4. Ideal: 1-3 números altos por jogo")
    print("5. Soma ideal: entre 180-240")
    print("6. Diversifique entre par e ímpar")
    print("\n⚠️  Lembre-se: São apenas estatísticas!")
    print("   A sorte ainda é o fator principal.")
    print("="*60)
    
    # Oferecer para gerar mais jogos
    resposta = input("\n🎰 Deseja gerar mais jogos? (s/n): ").strip().lower()
    if resposta == 's':
        try:
            qtd = int(input("Quantos jogos? (1-20): "))
            qtd = max(1, min(20, qtd))
            
            print(f"\n🎲 Gerando {qtd} jogos com método híbrido:")
            print("-"*40)
            
            jogos = otimizador.metodo_hibrido(qtd)
            for i, jogo in enumerate(jogos, 1):
                soma = sum(jogo)
                altos = sum(1 for n in jogo if n >= 35)
                print(f"Jogo {i:2d}: {', '.join(f'{n:2d}' for n in jogo)} | Soma: {soma:3d} | Altos: {altos}")
        
        except:
            print("⚠️  Entrada inválida, saindo...")

if __name__ == "__main__":
    main()
