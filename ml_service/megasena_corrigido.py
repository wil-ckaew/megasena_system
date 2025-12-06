#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA-SENA OTMIZADOR - Versão corrigida para formato n1,n2,n3,n4,n5,n6
Autor: Wil Ckaew
Versão: 2.1
Data: Dez 2024
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
from collections import Counter, defaultdict
import warnings
from sklearn.linear_model import LinearRegression
import statistics
import sys
import os

warnings.filterwarnings('ignore')

class MegaSenaCorrigido:
    def __init__(self, csv_path='resultados_megasena.csv'):
        """Inicializa o otimizador com formato n1,n2,n3,n4,n5,n6"""
        self.csv_path = csv_path
        
        print(f"📁 Carregando: {csv_path}")
        
        try:
            self.df = pd.read_csv(csv_path)
            print(f"✅ Dados carregados: {len(self.df)} sorteios históricos")
            
            # Verificar formato
            print(f"📋 Colunas detectadas: {list(self.df.columns)}")
            
            # Usar colunas n1, n2, n3, n4, n5, n6
            self.colunas_numeros = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
            
            # Verificar se as colunas existem
            colunas_faltantes = [col for col in self.colunas_numeros if col not in self.df.columns]
            if colunas_faltantes:
                print(f"⚠️  Colunas faltando: {colunas_faltantes}")
                print("🔍 Tentando detectar colunas alternativas...")
                
                # Procurar colunas numéricas
                colunas_numericas = []
                for col in self.df.columns:
                    try:
                        # Verificar se é numérica
                        if pd.api.types.is_numeric_dtype(self.df[col]):
                            colunas_numericas.append(col)
                    except:
                        pass
                
                if len(colunas_numericas) >= 6:
                    self.colunas_numeros = colunas_numericas[:6]
                    print(f"✅ Usando colunas numéricas: {self.colunas_numeros}")
                else:
                    # Usar últimas 6 colunas (assumindo que são os números)
                    todas_colunas = list(self.df.columns)
                    self.colunas_numeros = todas_colunas[-6:] if len(todas_colunas) >= 6 else todas_colunas
                    print(f"⚠️  Usando últimas colunas: {self.colunas_numeros}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            print("📊 Gerando dados de exemplo...")
            self.gerar_dados_exemplo()
        
        self.todos_numeros = list(range(1, 61))
        self.analise = {}
        self.preparar_dados()
    
    def gerar_dados_exemplo(self):
        """Gera dados de exemplo"""
        print("📊 Gerando dados de exemplo realistas...")
        np.random.seed(42)
        dados = []
        
        # Gerar 100 sorteios realistas
        for concurso in range(1, 101):
            while True:
                # Distribuição realista: 1-4 números altos (35-60)
                n_altos = random.choices([1, 2, 3, 4], weights=[0.2, 0.4, 0.3, 0.1])[0]
                n_baixos = 6 - n_altos
                
                # Gerar números únicos
                altos = sorted(np.random.choice(range(35, 61), n_altos, replace=False))
                baixos = sorted(np.random.choice(range(1, 35), n_baixos, replace=False))
                
                jogo = sorted(baixos + altos)
                soma = sum(jogo)
                
                # Verificar critérios realistas
                if 180 <= soma <= 240 and len(set(jogo)) == 6:
                    break
            
            # Data fictícia
            data = f"{(concurso % 28) + 1:02d}/{(concurso % 12) + 1:02d}/2024"
            
            dados.append({
                'Concurso': 2800 + concurso,
                'Data': data,
                'n1': jogo[0],
                'n2': jogo[1],
                'n3': jogo[2],
                'n4': jogo[3],
                'n5': jogo[4],
                'n6': jogo[5]
            })
        
        self.df = pd.DataFrame(dados)
        print(f"✅ {len(dados)} sorteios de exemplo gerados")
    
    def preparar_dados(self):
        """Prepara e analisa todos os dados históricos"""
        print("\n📊 Analisando dados históricos...")
        
        try:
            # Converter para inteiros
            for col in self.colunas_numeros:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0).astype(int)
            
            # 1. Análise de Frequência
            frequencias = Counter()
            for col in self.colunas_numeros:
                if col in self.df.columns:
                    frequencias.update(self.df[col].values)
            
            # Normalizar frequências
            total_sorteios = len(self.df)
            frequencias_norm = {num: count/total_sorteios for num, count in frequencias.items()}
            
            # 2. Cálculo de Atrasos
            atrasos = {}
            for num in self.todos_numeros:
                # Encontrar última ocorrência
                mask = (self.df[self.colunas_numeros] == num).any(axis=1)
                if mask.any():
                    ultimo_idx = mask[mask].index.max()
                    atraso = total_sorteios - ultimo_idx
                else:
                    atraso = total_sorteios + 10
                atrasos[num] = atraso
            
            # 3. Padrões por Posição
            padroes_posicao = {}
            for i, col in enumerate(self.colunas_numeros):
                if col in self.df.columns:
                    valores = self.df[col].values
                    if len(valores) > 0:
                        try:
                            moda = statistics.mode(valores)
                        except:
                            moda = np.argmax(np.bincount(valores))
                        
                        padroes_posicao[i] = {
                            'media': np.mean(valores),
                            'mediana': np.median(valores),
                            'std': np.std(valores),
                            'min': np.min(valores),
                            'max': np.max(valores),
                            'moda': moda,
                            'comuns': Counter(valores).most_common(5)
                        }
            
            # 4. Análise de Pares frequentes
            todos_numeros_jogo = []
            for _, row in self.df.iterrows():
                jogo = sorted([row[col] for col in self.colunas_numeros if col in self.df.columns])
                if len(jogo) == 6:
                    todos_numeros_jogo.append(jogo)
            
            # Pares frequentes
            pares_frequentes = Counter()
            for jogo in todos_numeros_jogo:
                for i in range(len(jogo)):
                    for j in range(i+1, len(jogo)):
                        par = tuple(sorted([jogo[i], jogo[j]]))
                        pares_frequentes[par] += 1
            
            # 5. Distribuição de números altos (35-60)
            numeros_altos = [num for num in self.todos_numeros if num >= 35]
            jogos_com_altos = []
            for jogo in todos_numeros_jogo:
                altos_no_jogo = sum(1 for num in jogo if num >= 35)
                jogos_com_altos.append(altos_no_jogo)
            
            distribuicao_altos = Counter(jogos_com_altos)
            
            # 6. Análise de Somas
            somas = [sum(jogo) for jogo in todos_numeros_jogo]
            
            # 7. Números quentes e frios (últimos 10 sorteios)
            if len(todos_numeros_jogo) >= 10:
                ultimos_10 = todos_numeros_jogo[-10:]
                numeros_ultimos = []
                for jogo in ultimos_10:
                    numeros_ultimos.extend(jogo)
                
                quentes = Counter(numeros_ultimos).most_common(15)
                todos_numeros_set = set(self.todos_numeros)
                frios_set = todos_numeros_set - set([num for num, _ in quentes])
                frios = [(num, 0) for num in sorted(frios_set)]
            else:
                quentes = frequencias.most_common(15)
                frios = [(num, count) for num, count in frequencias.most_common()[-15:]]
            
            self.analise = {
                'frequencias': frequencias,
                'frequencias_norm': frequencias_norm,
                'atrasos': atrasos,
                'padroes_posicao': padroes_posicao,
                'pares_frequentes': pares_frequentes.most_common(30),
                'distribuicao_altos': distribuicao_altos,
                'somas': {
                    'media': np.mean(somas) if somas else 0,
                    'std': np.std(somas) if somas else 0,
                    'min': np.min(somas) if somas else 0,
                    'max': np.max(somas) if somas else 0,
                },
                'todos_jogos': todos_numeros_jogo,
                'total_sorteios': total_sorteios,
                'numeros_quentes': quentes,
                'numeros_frios': frios[:15]
            }
            
            print("✅ Análise concluída com sucesso!")
            return self.analise
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def metodo_caravaca(self, dia=None):
        """Implementa o método de Caravaca baseado no dia do mês"""
        if dia is None:
            dia = datetime.now().day
        
        # Fórmula adaptada de Caravaca
        numeros_base = []
        
        # Fator do mês também
        mes = datetime.now().month
        fator_base = (dia * mes) % 60
        if fator_base == 0:
            fator_base = 7
        
        # Gerar 6 números usando diferentes fórmulas
        formulas = [
            lambda i: (fator_base * i + dia) % 60,
            lambda i: (fator_base + i * 7) % 60,
            lambda i: (dia * 13 - i * 3) % 60,
            lambda i: (mes * 11 + i * 5) % 60,
            lambda i: (fator_base * 3 - i * 2) % 60,
            lambda i: (dia * 17 + mes * 3 + i * 7) % 60
        ]
        
        for i, formula in enumerate(formulas):
            num = formula(i+1)
            if num <= 0:
                num = abs(num) + 1
            if num > 60:
                num = num % 60
                if num == 0:
                    num = 1
            
            # Garantir que temos números altos nas últimas posições
            if i >= 3:  # Últimos 3 números tendem a ser mais altos
                if num < 30:
                    num += random.randint(15, 30)
            
            numeros_base.append(num)
        
        # Garantir números únicos e válidos
        numeros_unicos = []
        for num in numeros_base:
            num = max(1, min(60, int(num)))
            if num not in numeros_unicos:
                numeros_unicos.append(num)
        
        # Completar até 6 números se necessário
        while len(numeros_unicos) < 6:
            novo_num = random.randint(1, 60)
            if novo_num not in numeros_unicos:
                numeros_unicos.append(novo_num)
        
        # Ordenar e ajustar distribuição
        numeros_ordenados = sorted(numeros_unicos[:6])
        
        # Garantir pelo menos 1 número alto (≥35)
        altos = sum(1 for n in numeros_ordenados if n >= 35)
        if altos == 0:
            # Substituir o maior número baixo por um alto
            numeros_baixos = [n for n in numeros_ordenados if n < 35]
            if numeros_baixos:
                idx = numeros_ordenados.index(max(numeros_baixos))
                while True:
                    novo_alto = random.randint(35, 60)
                    if novo_alto not in numeros_ordenados:
                        numeros_ordenados[idx] = novo_alto
                        break
                numeros_ordenados.sort()
        
        return numeros_ordenados
    
    def metodo_estatistico(self, quantidade=1):
        """Gera jogos baseados em estatísticas históricas"""
        jogos_gerados = []
        
        for _ in range(quantidade):
            jogo = []
            
            # 1. Escolher números baseados em múltiplos fatores
            probabilidades = []
            for num in self.todos_numeros:
                # Fatores:
                freq_score = self.analise['frequencias_norm'].get(num, 0.001)
                atraso = self.analise['atrasos'][num]
                atraso_score = min(1.0, atraso / (self.analise['total_sorteios'] * 0.3))
                
                # Verificar se é número quente
                quente_score = 1.0 if any(num == q[0] for q in self.analise['numeros_quentes'][:5]) else 0.5
                
                # Verificar se é número frio
                frio_score = 1.5 if any(num == f[0] for f in self.analise['numeros_frios'][:5]) else 1.0
                
                # Score final
                score = (0.3 * freq_score) + (0.3 * atraso_score) + (0.2 * quente_score) + (0.2 * frio_score)
                probabilidades.append(score)
            
            # Normalizar probabilidades
            prob_sum = sum(probabilidades)
            if prob_sum > 0:
                probabilidades = [p/prob_sum for p in probabilidades]
            else:
                probabilidades = [1/60] * 60
            
            # 2. Escolher 6 números únicos
            tentativas = 0
            while len(jogo) < 6 and tentativas < 100:
                num = np.random.choice(self.todos_numeros, p=probabilidades)
                if num not in jogo:
                    jogo.append(num)
                tentativas += 1
            
            # Completar se necessário
            while len(jogo) < 6:
                novo_num = random.randint(1, 60)
                if novo_num not in jogo:
                    jogo.append(novo_num)
            
            jogo.sort()
            
            # 3. Balancear números altos baseado na distribuição real
            altos = sum(1 for n in jogo if n >= 35)
            
            # Distribuição ideal baseada nos dados reais
            dist_real = self.analise['distribuicao_altos']
            if dist_real:
                # Pegar a quantidade mais comum de números altos
                mais_comum = max(dist_real.items(), key=lambda x: x[1])[0]
                if altos < mais_comum:
                    # Adicionar mais altos
                    falta = mais_comum - altos
                    numeros_para_trocar = [n for n in jogo if n < 30]
                    for i in range(min(falta, len(numeros_para_trocar))):
                        idx = jogo.index(numeros_para_trocar[i])
                        while True:
                            novo_alto = random.randint(35, 60)
                            if novo_alto not in jogo:
                                jogo[idx] = novo_alto
                                break
                    jogo.sort()
            
            # 4. Verificar soma
            soma = sum(jogo)
            soma_media = self.analise['somas']['media']
            soma_std = self.analise['somas']['std']
            
            # Ajustar se soma muito extrema
            if soma_std > 0 and (soma < soma_media - 2.5*soma_std or soma > soma_media + 2.5*soma_std):
                jogo = self.rebalancear_jogo(jogo, soma_media)
            
            jogos_gerados.append(jogo)
        
        return jogos_gerados if quantidade > 1 else jogos_gerados[0]
    
    def rebalancear_jogo(self, jogo, soma_alvo):
        """Rebalanceia um jogo para ter soma mais próxima da média"""
        nova_lista = jogo.copy()
        soma_atual = sum(nova_lista)
        
        # Ordem de substituição
        for tentativa in range(15):
            if abs(soma_atual - soma_alvo) < 30:
                break
            
            idx = random.randint(0, 5)
            num_antigo = nova_lista[idx]
            
            # Determinar direção do ajuste
            if soma_atual > soma_alvo + 30:
                # Muito alto, precisa diminuir
                candidatos = [n for n in range(1, num_antigo) 
                            if n not in nova_lista]
            elif soma_atual < soma_alvo - 30:
                # Muito baixo, precisa aumentar
                candidatos = [n for n in range(num_antigo + 1, 61) 
                            if n not in nova_lista]
            else:
                break
            
            if candidatos:
                novo_num = random.choice(candidatos)
                nova_lista[idx] = novo_num
                nova_lista.sort()
                soma_atual = sum(nova_lista)
        
        return nova_lista
    
    def metodo_ia_avancado(self, quantidade=1):
        """Usa técnicas de IA/ML para prever números"""
        jogos_gerados = []
        
        # Verificar se temos dados suficientes
        if len(self.analise['todos_jogos']) < 15:
            print("⚠️  Dados insuficientes para IA, usando método estatístico")
            return self.metodo_estatistico(quantidade)
        
        try:
            # Preparar dados para ML
            X = []
            y = []
            
            jogos = self.analise['todos_jogos']
            for i in range(len(jogos) - 1):
                jogo_atual = jogos[i]
                proximo_jogo = jogos[i + 1]
                
                # Features: estatísticas do jogo atual
                features = [
                    np.mean(jogo_atual),
                    np.std(jogo_atual),
                    min(jogo_atual),
                    max(jogo_atual),
                    sum(1 for n in jogo_atual if n >= 35),
                    sum(1 for n in jogo_atual if n <= 20),
                    jogo_atual[2],  # Terceiro número
                    (jogo_atual[5] - jogo_atual[0])  # Amplitude
                ]
                
                X.append(features)
                y.append(proximo_jogo)
            
            X = np.array(X)
            y = np.array(y)
            
            # Para cada posição, treinar um modelo
            modelos = []
            for pos in range(6):
                modelo = LinearRegression()
                modelo.fit(X, y[:, pos])
                modelos.append(modelo)
            
            # Gerar jogos
            for _ in range(quantidade):
                # Usar último jogo histórico para prever
                ultimo_jogo = jogos[-1]
                
                # Features do último jogo
                ultimo_features = [
                    np.mean(ultimo_jogo),
                    np.std(ultimo_jogo),
                    min(ultimo_jogo),
                    max(ultimo_jogo),
                    sum(1 for n in ultimo_jogo if n >= 35),
                    sum(1 for n in ultimo_jogo if n <= 20),
                    ultimo_jogo[2],
                    (ultimo_jogo[5] - ultimo_jogo[0])
                ]
                
                # Prever próximo jogo
                predicoes = []
                for modelo in modelos:
                    pred = modelo.predict([ultimo_features])[0]
                    pred = max(1, min(60, int(round(pred))))
                    predicoes.append(pred)
                
                # Garantir números únicos
                predicoes = list(set(predicoes))
                
                # Completar até 6 números únicos
                while len(predicoes) < 6:
                    # Escolher baseado em estatísticas
                    pesos = []
                    for num in self.todos_numeros:
                        if num not in predicoes:
                            freq = self.analise['frequencias_norm'].get(num, 0.001)
                            atraso = self.analise['atrasos'][num]
                            atraso_score = min(1.0, atraso / 30)
                            peso = freq + atraso_score
                            pesos.append((num, peso))
                    
                    # Escolher número com maior peso
                    if pesos:
                        pesos.sort(key=lambda x: x[1], reverse=True)
                        novo_num = pesos[0][0]
                        predicoes.append(novo_num)
                    else:
                        novo_num = random.randint(1, 60)
                        if novo_num not in predicoes:
                            predicoes.append(novo_num)
                
                # Ordenar e limitar a 6
                jogo = sorted(predicoes[:6])
                
                # Balanceamento final
                jogo = self.balancear_jogo_final(jogo)
                
                jogos_gerados.append(jogo)
                
        except Exception as e:
            print(f"⚠️  Erro no método IA: {e}")
            print("   Usando método estatístico como fallback...")
            return self.metodo_estatistico(quantidade)
        
        return jogos_gerados if quantidade > 1 else jogos_gerados[0]
    
    def metodo_hibrido(self, quantidade=1):
        """Combina todos os métodos para melhor resultado"""
        jogos_gerados = []
        
        for _ in range(quantidade):
            # Gerar jogos com diferentes métodos
            jogo_caravaca = self.metodo_caravaca()
            jogo_estatistico = self.metodo_estatistico()
            jogo_ia = self.metodo_ia_avancado()
            
            # Combinar todos os números
            todos_numeros = jogo_caravaca + jogo_estatistico + jogo_ia
            
            # Sistema de votação ponderada
            votos = {}
            pesos_metodo = {'caravaca': 1.0, 'estatistico': 1.5, 'ia': 2.0}
            
            for metodo, jogo in [('caravaca', jogo_caravaca), 
                                 ('estatistico', jogo_estatistico), 
                                 ('ia', jogo_ia)]:
                peso = pesos_metodo[metodo]
                for num in jogo:
                    if num not in votos:
                        votos[num] = 0
                    votos[num] += peso
            
            # Adicionar peso por frequência histórica
            for num in votos:
                freq = self.analise['frequencias_norm'].get(num, 0.001)
                atraso = self.analise['atrasos'][num]
                
                # Números atrasados ganham bonus
                atraso_bonus = min(2.0, atraso / 15)
                
                votos[num] += (freq * 10) + atraso_bonus
            
            # Ordenar por votos
            numeros_ordenados = sorted(votos.items(), key=lambda x: x[1], reverse=True)
            
            # Escolher top 6
            jogo_final = []
            for num, _ in numeros_ordenados[:8]:  # Pegar 8 para ter opções
                if len(jogo_final) < 6 and num not in jogo_final:
                    jogo_final.append(num)
            
            # Completar se necessário
            while len(jogo_final) < 6:
                for num, _ in numeros_ordenados:
                    if num not in jogo_final:
                        jogo_final.append(num)
                        break
            
            jogo_final.sort()
            
            # Aplicar balanceamento final
            jogo_final = self.balancear_jogo_final(jogo_final)
            
            jogos_gerados.append(jogo_final)
        
        return jogos_gerados if quantidade > 1 else jogos_gerados[0]
    
    def balancear_jogo_final(self, jogo):
        """Balanceamento final do jogo gerado"""
        jogo_balanceado = jogo.copy()
        
        # 1. Verificar números altos (≥35) baseado na distribuição real
        altos = sum(1 for n in jogo_balanceado if n >= 35)
        
        # Usar distribuição real dos dados históricos
        dist_real = self.analise['distribuicao_altos']
        if dist_real:
            # Calcular média de números altos nos dados reais
            total_jogos = sum(dist_real.values())
            media_altos_real = sum(k * v for k, v in dist_real.items()) / total_jogos
            
            # Ajustar para ficar próximo da média real
            if altos < int(media_altos_real):
                # Adicionar números altos
                falta = int(media_altos_real) - altos
                numeros_baixos = [n for n in jogo_balanceado if n < 35]
                for i in range(min(falta, len(numeros_baixos))):
                    idx = jogo_balanceado.index(numeros_baixos[i])
                    while True:
                        novo_alto = random.randint(35, 60)
                        if novo_alto not in jogo_balanceado:
                            jogo_balanceado[idx] = novo_alto
                            break
        
        # 2. Verificar números baixos (≤20)
        baixos = sum(1 for n in jogo_balanceado if n <= 20)
        if baixos < 1:
            # Adicionar um número baixo
            idx_para_substituir = random.randint(0, 5)
            while True:
                novo_baixo = random.randint(1, 20)
                if novo_baixo not in jogo_balanceado:
                    jogo_balanceado[idx_para_substituir] = novo_baixo
                    break
        
        # 3. Verificar soma
        soma = sum(jogo_balanceado)
        soma_media = self.analise['somas']['media']
        
        if soma_media > 0 and abs(soma - soma_media) > 50:
            # Ajuste leve
            jogo_balanceado = self.rebalancear_jogo(jogo_balanceado, soma_media)
        
        jogo_balanceado.sort()
        return jogo_balanceado
    
    def gerar_relatorio(self):
        """Gera relatório completo da análise"""
        print("\n" + "="*65)
        print("📈 RELATÓRIO DE ANÁLISE MEGA-SENA - FORMATO n1-n6")
        print("="*65)
        
        if not self.analise:
            print("❌ Análise não disponível. Verifique os dados.")
            return
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Total de sorteios analisados: {self.analise['total_sorteios']}")
        
        # Verificar se há coluna de data
        if 'Data' in self.df.columns:
            print(f"   • Período dos dados: {self.df['Data'].iloc[-1]} a {self.df['Data'].iloc[0]}")
        
        print(f"\n🎯 NÚMEROS MAIS FREQUENTES (TOP 10):")
        for i, (num, freq) in enumerate(self.analise['frequencias'].most_common(10), 1):
            perc = (freq / self.analise['total_sorteios']) * 100
            print(f"   {i:2d}. Nº {num:2d}: {freq:3d} vezes ({perc:.1f}%)")
        
        print(f"\n⏰ NÚMEROS MAIS ATRASADOS (TOP 10):")
        atrasos_ordenados = sorted(self.analise['atrasos'].items(), key=lambda x: x[1], reverse=True)
        for i, (num, atraso) in enumerate(atrasos_ordenados[:10], 1):
            print(f"   {i:2d}. Nº {num:2d}: {atraso:3d} sorteios sem aparecer")
        
        print(f"\n🔥 NÚMEROS QUENTES (últimos sorteios):")
        for i, (num, freq) in enumerate(self.analise['numeros_quentes'][:10], 1):
            print(f"   {i:2d}. Nº {num:2d}: {freq:2d} aparições recentes")
        
        print(f"\n❄️  NÚMEROS FRIOS (pouco sorteados):")
        for i, (num, freq) in enumerate(self.analise['numeros_frios'][:10], 1):
            print(f"   {i:2d}. Nº {num:2d}: {freq:2d} aparições totais")
        
        print(f"\n🔢 DISTRIBUIÇÃO DE NÚMEROS ALTOS (35-60):")
        if self.analise['distribuicao_altos']:
            for qtd_altos in sorted(self.analise['distribuicao_altos'].keys()):
                frequencia = self.analise['distribuicao_altos'][qtd_altos]
                if frequencia > 0:
                    perc = (frequencia / self.analise['total_sorteios']) * 100
                    print(f"   {qtd_altos} número(s) alto(s): {frequencia:3d} vezes ({perc:.1f}%)")
        
        print(f"\n💰 SOMA DOS NÚMEROS POR JOGO:")
        print(f"   • Média: {self.analise['somas']['media']:.1f}")
        print(f"   • Mínima: {self.analise['somas']['min']}")
        print(f"   • Máxima: {self.analise['somas']['max']}")
        print(f"   • Desvio padrão: {self.analise['somas']['std']:.1f}")
        print(f"   • Faixa ideal: {int(self.analise['somas']['media'] - 1.5*self.analise['somas']['std'])} "
              f"a {int(self.analise['somas']['media'] + 1.5*self.analise['somas']['std'])}")
        
        print(f"\n🤝 PARES MAIS FREQUENTES:")
        for i, (par, freq) in enumerate(self.analise['pares_frequentes'][:8], 1):
            print(f"   {i:2d}. {par[0]:2d} - {par[1]:2d}: {freq:3d} vezes juntos")
        
        print(f"\n📅 HOJE: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"   • Dia do mês: {datetime.now().day}")
        print(f"   • Mês: {datetime.now().month}")
        print("="*65)
    
    def gerar_jogos_otimizados(self, quantidade=5, metodo='hibrido'):
        """Gera múltiplos jogos otimizados"""
        print(f"\n🎲 GERANDO {quantidade} JOGOS OTMIZADOS (Método: {metodo.upper()})")
        print("="*65)
        
        if metodo == 'caravaca':
            jogos = [self.metodo_caravaca() for _ in range(quantidade)]
        elif metodo == 'estatistico':
            jogos = self.metodo_estatistico(quantidade)
        elif metodo == 'ia':
            jogos = self.metodo_ia_avancado(quantidade)
        else:  # hibrido
            jogos = self.metodo_hibrido(quantidade)
        
        # Exibir jogos com estatísticas
        print(f"{'Jogo':^5} {'Números':^45} {'Soma':^6} {'Altos':^6} {'Pares':^6}")
        print("-"*65)
        
        todas_somas = []
        todos_altos = []
        todos_pares = []
        
        for i, jogo in enumerate(jogos, 1):
            soma = sum(jogo)
            altos = sum(1 for n in jogo if n >= 35)
            pares = sum(1 for n in jogo if n % 2 == 0)
            
            todas_somas.append(soma)
            todos_altos.append(altos)
            todos_pares.append(pares)
            
            numeros_str = ', '.join(f'{n:2d}' for n in jogo)
            print(f"{i:^5} {numeros_str:^45} {soma:^6} {altos:^6} {pares:^6}")
        
        # Estatísticas dos jogos gerados
        print("\n" + "="*65)
        print("📊 ESTATÍSTICAS DOS JOGOS GERADOS:")
        print("="*65)
        
        if todas_somas:
            print(f"• Soma média: {sum(todas_somas)/len(todas_somas):.1f}")
            print(f"• Média de números altos (≥35): {sum(todos_altos)/len(todos_altos):.1f}")
            print(f"• Média de números pares: {sum(todos_pares)/len(todos_pares):.1f}")
            
            # Distribuição de números
            todos_numeros_jogos = []
            for jogo in jogos:
                todos_numeros_jogos.extend(jogo)
            
            contagem = Counter(todos_numeros_jogos)
            print(f"\n• Números mais frequentes nos jogos gerados:")
            for num, freq in contagem.most_common(10):
                print(f"  Nº {num:2d}: {freq:2d} vezes")
        
        return jogos

def main():
    """Função principal"""
    print("\n" + "="*65)
    print("🎰 MEGA-SENA OTMIZADOR - VERSÃO CORRIGIDA (n1-n6)")
    print("="*65)
    print("📁 Usando arquivo: resultados_megasena.csv")
    
    # Inicializar otimizador
    otimizador = MegaSenaCorrigido()
    
    # Gerar relatório
    otimizador.gerar_relatorio()
    
    # Gerar jogos com método híbrido (recomendado)
    print("\n" + "="*65)
    print("💡 JOGOS RECOMENDADOS (Método Híbrido):")
    print("="*65)
    
    try:
        jogos_hibrido = otimizador.gerar_jogos_otimizados(quantidade=8, metodo='hibrido')
    except Exception as e:
        print(f"❌ Erro ao gerar jogos: {e}")
        jogos_hibrido = []
    
    # Mostrar também jogos dos outros métodos
    print("\n" + "="*65)
    print("🔍 COMPARAÇÃO DE MÉTODOS (1 jogo cada):")
    print("="*65)
    
    metodos = [
        ("Caravaca (dia/mês)", 'caravaca'),
        ("Estatístico", 'estatistico'),
        ("IA Avançado", 'ia'),
    ]
    
    for nome, metodo in metodos:
        try:
            if metodo == 'caravaca':
                jogo = otimizador.metodo_caravaca()
            elif metodo == 'estatistico':
                jogo = otimizador.metodo_estatistico(1)
            else:  # ia
                jogo = otimizador.metodo_ia_avancado(1)
            
            soma = sum(jogo)
            altos = sum(1 for n in jogo if n >= 35)
            pares = sum(1 for n in jogo if n % 2 == 0)
            
            print(f"\n{nome}:")
            print(f"  Números: {', '.join(f'{n:2d}' for n in jogo)}")
            print(f"  Soma: {soma:3d} | Altos: {altos} | Pares: {pares}")
        except Exception as e:
            print(f"\n{nome}: Erro - {e}")
    
    # Dicas finais
    print("\n" + "="*65)
    print("💡 DICAS ESTRATÉGICAS:")
    print("="*65)
    print("✅ Sistema agora otimizado para seu formato n1-n6")
    print("✅ Garantia de números altos (35-60) baseada nos dados reais")
    print("✅ Análise completa de 52 sorteios históricos")
    print("✅ 4 métodos diferentes de geração")
    print("\n⚠️  Lembre-se: São apenas estatísticas!")
    print("   A sorte ainda é o fator principal nos jogos de loteria.")
    print("   Jogue com responsabilidade!")
    print("="*65)
    
    # Salvar sugestões em arquivo
    try:
        salvar_sugestoes = input("\n💾 Deseja salvar estas sugestões em arquivo? (s/n): ")
        if salvar_sugestoes.lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sugestoes_megasena_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("SUGESTÕES MEGA-SENA - GERADAS POR IA/ESTATÍSTICA\n")
                f.write("="*60 + "\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Sorteios analisados: {otimizador.analise['total_sorteios']}\n")
                f.write(f"Formato do CSV: n1, n2, n3, n4, n5, n6\n\n")
                
                f.write("JOGOS RECOMENDADOS (Híbrido):\n")
                for i, jogo in enumerate(jogos_hibrido, 1):
                    f.write(f"Jogo {i:2d}: {', '.join(f'{n:2d}' for n in jogo)}\n")
            
            print(f"✅ Sugestões salvas em: {filename}")
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
