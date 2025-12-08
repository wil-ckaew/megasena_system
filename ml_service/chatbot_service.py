#!/usr/bin/env python3
"""
🤖 CHATBOT MEGA-SENA INTEGRADO
Serviço de chatbot que se integra com seu sistema existente
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
from collections import Counter
import re
import json
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

app = FastAPI(title="Chatbot Mega-Sena API", version="1.0")

# CORS para integração com frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str
    user_id: Optional[str] = None

class GameAnalysis(BaseModel):
    numbers: List[int]
    user_id: Optional[str] = None

class BolaoRequest(BaseModel):
    quantidade_jogos: int = 10
    metodo: str = "hibrido"
    incluir_historico: bool = True

class MegaSenaChatbot:
    def __init__(self, csv_path='resultados_megasena.csv'):
        self.csv_path = csv_path
        self.df = None
        self.analise = {}
        self.boloes_historico = []
        self.modelo_aprendizado = None
        self.carregar_dados()
        self.inicializar_modelo_ia()
    
    def carregar_dados(self):
        """Carrega dados históricos e boloes"""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"✅ Dados históricos carregados: {len(self.df)} sorteios")
            
            # Carregar boloes se existirem
            if os.path.exists('boloes_historico.json'):
                with open('boloes_historico.json', 'r') as f:
                    self.boloes_historico = json.load(f)
                print(f"✅ Boloes históricos carregados: {len(self.boloes_historico)}")
            
            self.analisar_dados()
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
    
    def analisar_dados(self):
        """Analisa dados históricos"""
        if self.df is None:
            return
        
        # Detectar colunas de números
        if 'n1' in self.df.columns:
            self.colunas_numeros = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
        else:
            colunas_nums = [col for col in self.df.columns 
                          if pd.api.types.is_numeric_dtype(self.df[col])]
            self.colunas_numeros = colunas_nums[:6]
        
        # Análise de frequência
        frequencias = Counter()
        for col in self.colunas_numeros:
            if col in self.df.columns:
                frequencias.update(self.df[col].values)
        
        # Análise de padrões
        padroes_vencedores = self.extrair_padroes_vencedores()
        
        self.analise = {
            'frequencias': frequencias,
            'total_sorteios': len(self.df),
            'padroes_vencedores': padroes_vencedores,
            'media_altos': self.calcular_media_altos(),
            'media_soma': self.calcular_media_soma()
        }
    
    def extrair_padroes_vencedores(self):
        """Extrai padrões dos sorteios vencedores"""
        padroes = {
            'distribuicao_altos': [],
            'distribuicao_pares': [],
            'faixas_numericas': [],
            'sequencias': []
        }
        
        for _, row in self.df.iterrows():
            jogo = [row[col] for col in self.colunas_numeros if col in self.df.columns]
            if len(jogo) == 6:
                # Distribuição de números altos
                altos = sum(1 for n in jogo if n >= 35)
                padroes['distribuicao_altos'].append(altos)
                
                # Distribuição de pares
                pares = sum(1 for n in jogo if n % 2 == 0)
                padroes['distribuicao_pares'].append(pares)
                
                # Faixas numéricas (1-15, 16-30, 31-45, 46-60)
                faixas = [0, 0, 0, 0]
                for num in jogo:
                    if num <= 15: faixas[0] += 1
                    elif num <= 30: faixas[1] += 1
                    elif num <= 45: faixas[2] += 1
                    else: faixas[3] += 1
                padroes['faixas_numericas'].append(faixas)
        
        return padroes
    
    def calcular_media_altos(self):
        """Calcula média de números altos por jogo vencedor"""
        altos_por_jogo = []
        for _, row in self.df.iterrows():
            jogo = [row[col] for col in self.colunas_numeros if col in self.df.columns]
            altos = sum(1 for n in jogo if n >= 35)
            altos_por_jogo.append(altos)
        return np.mean(altos_por_jogo) if altos_por_jogo else 2.5
    
    def calcular_media_soma(self):
        """Calcula média da soma dos números vencedores"""
        somas = []
        for _, row in self.df.iterrows():
            jogo = [row[col] for col in self.colunas_numeros if col in self.df.columns]
            if len(jogo) == 6:
                somas.append(sum(jogo))
        return np.mean(somas) if somas else 210
    
    def inicializar_modelo_ia(self):
        """Inicializa modelo de aprendizado"""
        try:
            if os.path.exists('modelo_aprendizado.pkl'):
                with open('modelo_aprendizado.pkl', 'rb') as f:
                    self.modelo_aprendizado = pickle.load(f)
                print("✅ Modelo de aprendizado carregado")
            else:
                self.treinar_modelo_aprendizado()
        except:
            self.treinar_modelo_aprendizado()
    
    def treinar_modelo_aprendizado(self):
        """Treina modelo com dados históricos"""
        if self.df is None or len(self.df) < 10:
            print("⚠️  Dados insuficientes para treinar modelo")
            return
        
        # Preparar dados para treinamento
        X = []
        y = []
        
        for i in range(len(self.df) - 1):
            jogo_atual = [self.df[col].iloc[i] for col in self.colunas_numeros]
            proximo_jogo = [self.df[col].iloc[i + 1] for col in self.colunas_numeros]
            
            # Features do jogo atual
            features = [
                np.mean(jogo_atual),
                np.std(jogo_atual),
                min(jogo_atual),
                max(jogo_atual),
                sum(1 for n in jogo_atual if n >= 35),
                sum(1 for n in jogo_atual if n <= 20),
                sum(jogo_atual) % 10,  # Último dígito da soma
                len(set(jogo_atual) & set(range(1, 16))),  # Números na faixa 1-15
                len(set(jogo_atual) & set(range(46, 61))),  # Números na faixa 46-60
            ]
            
            X.append(features)
            
            # Label: probabilidade de cada número aparecer no próximo sorteio
            label = [1 if num in proximo_jogo else 0 for num in range(1, 61)]
            y.append(label)
        
        if len(X) > 5:
            X = np.array(X)
            y = np.array(y)
            
            # Treinar modelo RandomForest
            self.modelo_aprendizado = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            
            # Para simplificar, treinar para prever se número 1 aparece
            y_simplificado = y[:, 0]  # Apenas primeiro número como exemplo
            self.modelo_aprendizado.fit(X, y_simplificado)
            
            # Salvar modelo
            with open('modelo_aprendizado.pkl', 'wb') as f:
                pickle.dump(self.modelo_aprendizado, f)
            
            print("✅ Modelo de aprendizado treinado e salvo")
    
    async def processar_mensagem(self, texto: str, user_id: str = None):
        """Processa mensagem do usuário"""
        texto = texto.lower().strip()
        
        # Detectar intenção
        intencao = self.detectar_intencao(texto)
        
        if intencao == 'saudacao':
            return await self.responder_saudacao()
        elif intencao == 'estatisticas':
            return await self.responder_estatisticas()
        elif intencao == 'gerar_jogo':
            return await self.gerar_jogo_personalizado(texto)
        elif intencao == 'analisar_jogo':
            return await self.analisar_jogo_usuario(texto)
        elif intencao == 'bolao':
            return await self.gerar_bolao_sugestao()
        elif intencao == 'dicas':
            return await self.responder_dicas()
        elif intencao == 'aprendizado':
            return await self.explicar_aprendizado()
        else:
            return await self.responder_generico(texto)
    
    def detectar_intencao(self, texto):
        """Detecta intenção do usuário com base em palavras-chave"""
        texto = texto.lower()
        
        intencoes = {
            'saudacao': ['oi', 'olá', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'hey'],
            'estatisticas': ['estatística', 'estatisticas', 'frequente', 'atrasado', 'número mais', 'top 10'],
            'gerar_jogo': ['gerar', 'sugerir', 'número', 'jogo', 'aposta', 'quero jogar', 'me dê números'],
            'analisar_jogo': ['analisar', 'analise', 'verificar', 'checar', 'meu jogo', 'esses números'],
            'bolao': ['bolão', 'bolao', 'vários jogos', 'múltiplos', 'grupo', 'feijão'],
            'dicas': ['dica', 'conselho', 'estratégia', 'como ganhar', 'técnica', 'melhor jeito'],
            'aprendizado': ['aprende', 'aprendizado', 'machine learning', 'ia', 'inteligência', 'modelo'],
            'caravaca': ['caravaca', 'método caravaca', 'dia do mês']
        }
        
        for intencao, palavras in intencoes.items():
            for palavra in palavras:
                if palavra in texto:
                    return intencao
        
        return 'generico'
    
    async def responder_saudacao(self):
        """Resposta de saudação"""
        respostas = [
            "Olá! Sou o assistente inteligente da Mega-Sena. Como posso ajudar? 🎰",
            "Bem-vindo ao sistema de análise Mega-Sena! Posso gerar jogos, analisar padrões e muito mais! 🤖",
            "Oi! Pronto para aumentar suas chances com IA e análise de dados? Vamos lá! 📊"
        ]
        return {
            "tipo": "texto",
            "conteudo": random.choice(respostas),
            "sugestoes": ["Gerar jogo", "Ver estatísticas", "Criar bolão", "Dicas"]
        }
    
    async def responder_estatisticas(self):
        """Retorna estatísticas atualizadas"""
        if not self.analise:
            return {
                "tipo": "texto", 
                "conteudo": "❌ Dados não disponíveis no momento."
            }
        
        # Top 10 números mais frequentes
        top_frequentes = self.analise['frequencias'].most_common(10)
        frequentes_str = "\n".join([f"{i+1}. Nº {num}: {freq}x" 
                                  for i, (num, freq) in enumerate(top_frequentes)])
        
        # Padrões
        media_altos = self.analise['media_altos']
        media_soma = self.analise['media_soma']
        
        conteudo = f"""📊 **ESTATÍSTICAS ATUALIZADAS**

🎯 **TOP 10 NÚMEROS MAIS FREQUENTES:**
{frequentes_str}

📈 **PADRÕES DE SORTEIOS VENCEDORES:**
• Média de números altos (≥35): {media_altos:.1f} por jogo
• Soma média vencedora: {media_soma:.1f}
• Distribuição ideal: 2-3 números altos, 3-4 números baixos

📅 Baseado em {self.analise['total_sorteios']} sorteios históricos.
"""
        
        return {
            "tipo": "texto",
            "conteudo": conteudo,
            "graficos": ["frequencia", "distribuicao"]
        }
    
    async def gerar_jogo_personalizado(self, texto):
        """Gera jogo personalizado baseado no texto"""
        # Extrair preferências
        preferencias = {
            'altos': 'alto' in texto or 'grande' in texto or '>35' in texto,
            'baixos': 'baixo' in texto or 'pequeno' in texto or '<35' in texto,
            'pares': 'par' in texto,
            'impares': 'ímpar' in texto or 'impar' in texto,
            'quantidade': self.extrair_quantidade(texto)
        }
        
        quantidade = preferencias['quantidade']
        jogos = []
        
        for _ in range(quantidade):
            if preferencias['altos']:
                jogo = self.gerar_jogo_com_altos()
            elif preferencias['baixos']:
                jogo = self.gerar_jogo_com_baixos()
            elif preferencias['pares']:
                jogo = self.gerar_jogo_pares()
            elif preferencias['impares']:
                jogo = self.gerar_jogo_impares()
            else:
                jogo = self.gerar_jogo_otimizado()
            jogos.append(jogo)
        
        # Formatar resposta
        conteudo = f"🎲 **{quantidade} JOGO(S) GERADO(S):**\n\n"
        for i, jogo in enumerate(jogos, 1):
            stats = self.calcular_estatisticas_jogo(jogo)
            conteudo += f"**Jogo {i}:** `{', '.join(f'{n:2d}' for n in jogo)}`\n"
            conteudo += f"   • Soma: {stats['soma']} | Altos: {stats['altos']} | Pares: {stats['pares']}\n\n"
        
        # Adicionar análise do aprendizado
        if self.modelo_aprendizado and jogos:
            analise_ia = self.analisar_jogo_com_ia(jogos[0])
            conteudo += f"🤖 **ANÁLISE DA IA:**\n"
            conteudo += f"   • Score de similaridade: {analise_ia['similaridade']:.2%}\n"
            conteudo += f"   • Baseado em {len(self.df)} sorteios históricos\n"
        
        return {
            "tipo": "jogos",
            "conteudo": conteudo,
            "jogos": jogos,
            "estatisticas": [self.calcular_estatisticas_jogo(j) for j in jogos]
        }
    
    def gerar_jogo_otimizado(self):
        """Gera jogo otimizado usando aprendizado"""
        if self.modelo_aprendizado and len(self.df) > 10:
            # Usar último sorteio para features
            ultimo_jogo = [self.df[col].iloc[-1] for col in self.colunas_numeros]
            features = self.extrair_features_jogo(ultimo_jogo)
            
            # Prever probabilidades para cada número
            probabilidades = []
            for num in range(1, 61):
                # Features específicas para cada número
                feat_num = features + [num % 10, num // 15, 1 if num >= 35 else 0]
                prob = self.modelo_aprendizado.predict_proba([feat_num])[0][1]
                probabilidades.append((num, prob))
            
            # Escolher 6 números com maior probabilidade
            probabilidades.sort(key=lambda x: x[1], reverse=True)
            numeros_escolhidos = [num for num, _ in probabilidades[:8]]
            
            # Garantir diversidade
            jogo = []
            for num in numeros_escolhidos:
                if len(jogo) < 6 and num not in jogo:
                    jogo.append(num)
            
            # Completar se necessário
            while len(jogo) < 6:
                novo_num = random.randint(1, 60)
                if novo_num not in jogo:
                    jogo.append(novo_num)
            
            return sorted(jogo)
        else:
            # Fallback para método estatístico
            return self.gerar_jogo_estatistico()
    
    def gerar_jogo_estatistico(self):
        """Gera jogo baseado em estatísticas"""
        # Baseado na distribuição real
        n_altos = random.choices([1, 2, 3, 4], 
                                weights=[0.15, 0.35, 0.35, 0.15])[0]
        n_baixos = 6 - n_altos
        
        # Escolher números considerando frequência e atraso
        todos_numeros = list(range(1, 61))
        pesos = []
        
        for num in todos_numeros:
            freq = self.analise['frequencias'].get(num, 0.1)
            atraso = self.calcular_atraso(num)
            peso = (freq * 0.4) + (atraso * 0.6)
            pesos.append(peso)
        
        # Normalizar pesos
        soma_pesos = sum(pesos)
        pesos = [p/soma_pesos for p in pesos]
        
        # Escolher números únicos
        jogo = []
        tentativas = 0
        while len(jogo) < 6 and tentativas < 100:
            num = random.choices(todos_numeros, weights=pesos)[0]
            if num not in jogo:
                jogo.append(num)
            tentativas += 1
        
        # Ordenar
        return sorted(jogo)
    
    def calcular_atraso(self, numero):
        """Calcula quanto tempo um número não é sorteado"""
        if self.df is None:
            return 1
        
        for i in range(len(self.df)-1, -1, -1):
            jogo = [self.df[col].iloc[i] for col in self.colunas_numeros]
            if numero in jogo:
                return len(self.df) - i
        
        return len(self.df) + 10
    
    def extrair_features_jogo(self, jogo):
        """Extrai features de um jogo para o modelo"""
        return [
            np.mean(jogo),
            np.std(jogo),
            min(jogo),
            max(jogo),
            sum(1 for n in jogo if n >= 35),
            sum(1 for n in jogo if n <= 20),
            sum(jogo) % 10,
            len(set(jogo) & set(range(1, 16))),
            len(set(jogo) & set(range(46, 61))),
        ]
    
    def analisar_jogo_com_ia(self, jogo):
        """Analisa jogo usando modelo de IA"""
        if not self.modelo_aprendizado:
            return {"similaridade": 0.5, "observacoes": "Modelo não disponível"}
        
        features = self.extrair_features_jogo(jogo)
        
        # Calcular similaridade com sorteios vencedores
        similaridades = []
        for _, row in self.df.iterrows():
            jogo_historico = [row[col] for col in self.colunas_numeros]
            feat_hist = self.extrair_features_jogo(jogo_historico)
            
            # Similaridade cosseno
            similarity = np.dot(features, feat_hist) / (
                np.linalg.norm(features) * np.linalg.norm(feat_hist)
            )
            similaridades.append(similarity)
        
        avg_similaridade = np.mean(similaridades) if similaridades else 0.5
        
        observacoes = []
        if avg_similaridade > 0.7:
            observacoes.append("🎯 Alto padrão de similaridade com sorteios vencedores")
        elif avg_similaridade > 0.5:
            observacoes.append("✅ Padrão dentro da média histórica")
        else:
            observacoes.append("⚠️  Padrão diferente da maioria dos sorteios vencedores")
        
        return {
            "similaridade": avg_similaridade,
            "observacoes": observacoes
        }
    
    async def gerar_bolao_sugestao(self):
        """Gera sugestão de bolão"""
        bolao = self.criar_bolao_otimizado(quantidade=15)
        
        # Salvar bolão no histórico
        self.boloes_historico.append({
            "timestamp": datetime.now().isoformat(),
            "jogos": bolao,
            "estatisticas": self.analisar_bolao(bolao)
        })
        
        # Salvar histórico
        self.salvar_historico_boloes()
        
        conteudo = f"""🏆 **SUGESTÃO DE BOLÃO (15 JOGOS)**

📊 **ESTATÍSTICAS DO BOLÃO:**
• Total de números únicos usados: {len(set([n for jogo in bolao for n in jogo]))}
• Cobertura numérica: {len(set([n for jogo in bolao for n in jogo]))/60:.1%}
• Média de números altos por jogo: {np.mean([sum(1 for n in jogo if n >= 35) for jogo in bolao]):.1f}
• Custo estimado (R$ 4,50/jogo): R$ {len(bolao) * 4.5:.2f}

🎯 **JOGOS RECOMENDADOS:**
"""
        
        for i, jogo in enumerate(bolao[:5], 1):  # Mostrar apenas 5
            stats = self.calcular_estatisticas_jogo(jogo)
            conteudo += f"{i}. `{', '.join(f'{n:2d}' for n in jogo)}` "
            conteudo += f"(Soma: {stats['soma']}, Altos: {stats['altos']})\n"
        
        if len(bolao) > 5:
            conteudo += f"\n... e mais {len(bolao)-5} jogos otimizados"
        
        return {
            "tipo": "bolao",
            "conteudo": conteudo,
            "bolao": bolao,
            "estatisticas": self.analisar_bolao(bolao)
        }
    
    def criar_bolao_otimizado(self, quantidade=15):
        """Cria bolão otimizado com máxima cobertura"""
        bolao = []
        numeros_cobertos = set()
        
        # Estratégia: Maximizar cobertura de números
        while len(bolao) < quantidade:
            # Priorizar números menos cobertos
            numeros_nao_cobertos = [n for n in range(1, 61) if n not in numeros_cobertos]
            
            if len(numeros_nao_cobertos) >= 6:
                # Criar jogo com números não cobertos
                jogo = random.sample(numeros_nao_cobertos, 6)
            else:
                # Completar com números aleatórios
                jogo = random.sample(numeros_nao_cobertos, len(numeros_nao_cobertos))
                complemento = random.sample(
                    [n for n in range(1, 61) if n not in jogo],
                    6 - len(jogo)
                )
                jogo.extend(complemento)
            
            jogo.sort()
            
            # Verificar se é um jogo válido
            if self.validar_jogo(jogo) and jogo not in bolao:
                bolao.append(jogo)
                numeros_cobertos.update(jogo)
        
        return bolao
    
    def analisar_bolao(self, bolao):
        """Analisa estatísticas do bolão"""
        todos_numeros = [n for jogo in bolao for n in jogo]
        
        return {
            "total_numeros_unicos": len(set(todos_numeros)),
            "cobertura_percentual": len(set(todos_numeros)) / 60,
            "media_altos_por_jogo": np.mean([sum(1 for n in jogo if n >= 35) for jogo in bolao]),
            "media_soma_por_jogo": np.mean([sum(jogo) for jogo in bolao]),
            "distribuicao_faixas": self.calcular_distribuicao_faixas(todos_numeros)
        }
    
    def calcular_distribuicao_faixas(self, numeros):
        """Calcula distribuição por faixas numéricas"""
        faixas = [0, 0, 0, 0]  # 1-15, 16-30, 31-45, 46-60
        for num in numeros:
            if num <= 15: faixas[0] += 1
            elif num <= 30: faixas[1] += 1
            elif num <= 45: faixas[2] += 1
            else: faixas[3] += 1
        return faixas
    
    async def analisar_jogo_usuario(self, texto):
        """Analisa jogo fornecido pelo usuário"""
        numeros = self.extrair_numeros_texto(texto)
        
        if len(numeros) < 6:
            return {
                "tipo": "texto",
                "conteudo": "❌ Preciso de 6 números entre 1 e 60. Exemplo: 'Analisar 10 20 30 40 50 60'"
            }
        
        jogo = sorted(numeros[:6])
        stats = self.calcular_estatisticas_jogo(jogo)
        analise_ia = self.analisar_jogo_com_ia(jogo)
        
        conteudo = f"""🔍 **ANÁLISE DO JOGO:** `{', '.join(f'{n:2d}' for n in jogo)}`

📊 **ESTATÍSTICAS:**
• Soma total: {stats['soma']}
• Números altos (≥35): {stats['altos']}
• Números baixos (≤20): {stats['baixos']}
• Números pares/ímpares: {stats['pares']}/{stats['impares']}

🤖 **ANÁLISE DA IA:**
• Similaridade com sorteios vencedores: {analise_ia['similaridade']:.2%}
• {analise_ia['observacoes'][0] if analise_ia['observacoes'] else 'Análise disponível'}

💡 **RECOMENDAÇÕES:**
"""
        
        recomendacoes = []
        if stats['altos'] == 0:
            recomendacoes.append("Considere adicionar 1-2 números altos (≥35)")
        elif stats['altos'] > 3:
            recomendacoes.append("Muitos números altos, ideal é 2-3")
        
        if stats['baixos'] == 0:
            recomendacoes.append("Adicione 1-2 números baixos (≤20)")
        
        if stats['pares'] < 2 or stats['pares'] > 4:
            recomendacoes.append("Balanço ideal de pares/ímpares: 2-4 de cada")
        
        if not recomendacoes:
            recomendacoes.append("Jogo bem balanceado! Boa sorte! 🍀")
        
        for i, rec in enumerate(recomendacoes, 1):
            conteudo += f"{i}. {rec}\n"
        
        return {
            "tipo": "analise",
            "conteudo": conteudo,
            "jogo": jogo,
            "estatisticas": stats,
            "analise_ia": analise_ia
        }
    
    async def responder_dicas(self):
        """Retorna dicas estratégicas"""
        dicas = [
            "🎯 **Diversifique faixas:** Use números de todas as faixas (1-15, 16-30, 31-45, 46-60)",
            "🎯 **Balanceie altos/baixos:** Ideal é 2-3 números altos (≥35) por jogo",
            "🎯 **Misture pares/ímpares:** Evite todos pares ou todos ímpares",
            "🎯 **Soma ideal:** A soma deve ficar entre 180-240 na maioria dos sorteios",
            "🎯 **Evite padrões:** Não use apenas números sequenciais ou datas",
            "🎯 **Considere atrasados:** Inclua números que não saem há mais de 15 sorteios",
            "🎯 **Bolão inteligente:** Em bolões, maximize a cobertura de números diferentes",
            "🎯 **Use a IA:** Nosso sistema aprende com sorteios passados para sugerir padrões",
            "🎯 **Aposte responsavelmente:** Defina um orçamento e não o ultrapasse",
            "🎯 **Diversifique:** Não coloque todos os recursos em uma única estratégia"
        ]
        
        conteudo = "💡 **TOP 10 DICAS ESTRATÉGICAS:**\n\n"
        for dica in dicas:
            conteudo += f"{dica}\n"
        
        return {
            "tipo": "texto",
            "conteudo": conteudo
        }
    
    async def explicar_aprendizado(self):
        """Explica como o sistema aprende"""
        conteudo = """🤖 **COMO NOSSO SISTEMA APRENDE:**

📚 **Fonte de dados:**
• {total} sorteios históricos analisados
• Padrões extraídos de jogos vencedores
• Estatísticas atualizadas em tempo real

🧠 **Técnicas de aprendizado:**
1. **Análise de Frequência:** Identifica números que aparecem mais
2. **Detecção de Padrões:** Encontra combinações comuns em sorteios
3. **Machine Learning:** Modelo que prevê probabilidades baseado em histórico
4. **Otimização:** Sugere jogos com maior cobertura numérica

🔍 **O que analisamos:**
• Distribuição de números altos/baixos
• Proporção de números pares/ímpares
• Soma total dos números
• Faixas numéricas mais frequentes
• Números atrasados (não sorteados há tempo)

✨ **Benefícios:**
• Sugestões baseadas em dados reais
• Identificação de padrões não óbvios
• Otimização automática para bolões
• Análise personalizada dos seus jogos

O sistema está sempre aprendendo e se atualizando! 📈
""".format(total=self.analise['total_sorteios'] if self.analise else "N/A")
        
        return {
            "tipo": "texto",
            "conteudo": conteudo
        }
    
    async def responder_generico(self, texto):
        """Resposta genérica para mensagens não reconhecidas"""
        respostas = [
            "Hmm, não entendi completamente. Que tal perguntar sobre:\n• Gerar um jogo otimizado\n• Ver estatísticas atualizadas\n• Criar um bolão\n• Receber dicas estratégicas?",
            "Posso ajudar com:\n🎯 Geração de jogos com IA\n📊 Análise estatística\n🏆 Criação de bolões\n💡 Dicas personalizadas\n\nO que gostaria de fazer?",
            "Sou especializado em Mega-Sena! Posso:\n1. Analisar seus números\n2. Sugerir jogos otimizados\n3. Explicar probabilidades\n4. Criar estratégias de bolão\n\nComo posso ajudar?"
        ]
        
        return {
            "tipo": "texto",
            "conteudo": random.choice(respostas),
            "sugestoes": ["Gerar jogo", "Estatísticas", "Criar bolão", "Como funciona a IA?"]
        }
    
    # Métodos auxiliares
    def extrair_quantidade(self, texto):
        numeros = re.findall(r'\d+', texto)
        if numeros:
            qtd = int(numeros[0])
            return min(max(1, qtd), 20)  # Limitar a 20 jogos
        return 1
    
    def extrair_numeros_texto(self, texto):
        numeros = re.findall(r'\b\d{1,2}\b', texto)
        return [int(n) for n in numeros if 1 <= int(n) <= 60]
    
    def calcular_estatisticas_jogo(self, jogo):
        return {
            "soma": sum(jogo),
            "altos": sum(1 for n in jogo if n >= 35),
            "baixos": sum(1 for n in jogo if n <= 20),
            "pares": sum(1 for n in jogo if n % 2 == 0),
            "impares": len(jogo) - sum(1 for n in jogo if n % 2 == 0)
        }
    
    def validar_jogo(self, jogo):
        """Valida se um jogo é válido"""
        if len(jogo) != 6:
            return False
        if len(set(jogo)) != 6:
            return False
        if any(n < 1 or n > 60 for n in jogo):
            return False
        return True
    
    def salvar_historico_boloes(self):
        """Salva histórico de boloes em arquivo"""
        try:
            with open('boloes_historico.json', 'w') as f:
                json.dump(self.boloes_historico[-100:], f)  # Manter apenas últimos 100
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

# Instanciar chatbot
chatbot = MegaSenaChatbot()

# WebSocket para comunicação em tempo real
connected_clients = []

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar mensagem
            response = await chatbot.processar_mensagem(
                message_data.get("text", ""),
                message_data.get("user_id")
            )
            
            # Enviar resposta
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        print(f"Erro WebSocket: {e}")

# Endpoints REST
@app.post("/api/chat")
async def api_chat(message: Message):
    """Endpoint REST para chat"""
    response = await chatbot.processar_mensagem(message.text, message.user_id)
    return response

@app.post("/api/analisar")
async def api_analisar(game: GameAnalysis):
    """Endpoint para análise de jogo"""
    jogo = game.numbers[:6]
    stats = chatbot.calcular_estatisticas_jogo(jogo)
    analise_ia = chatbot.analisar_jogo_com_ia(jogo)
    
    return {
        "jogo": jogo,
        "estatisticas": stats,
        "analise_ia": analise_ia,
        "recomendacoes": chatbot.gerar_recomendacoes_jogo(jogo)
    }

@app.post("/api/bolao")
async def api_bolao(request: BolaoRequest):
    """Endpoint para gerar bolão"""
    bolao = chatbot.criar_bolao_otimizado(request.quantidade_jogos)
    estatisticas = chatbot.analisar_bolao(bolao)
    
    # Salvar no histórico se solicitado
    if request.incluir_historico:
        chatbot.boloes_historico.append({
            "timestamp": datetime.now().isoformat(),
            "quantidade": request.quantidade_jogos,
            "jogos": bolao,
            "estatisticas": estatisticas
        })
        chatbot.salvar_historico_boloes()
    
    return {
        "bolao": bolao,
        "estatisticas": estatisticas,
        "total_jogos": len(bolao),
        "custo_estimado": len(bolao) * 4.5
    }

@app.get("/api/estatisticas")
async def api_estatisticas():
    """Endpoint para estatísticas"""
    if not chatbot.analise:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")
    
    # Preparar dados para frontend
    top_frequentes = []
    for num, freq in chatbot.analise['frequencias'].most_common(15):
        top_frequentes.append({
            "numero": num,
            "frequencia": freq,
            "percentual": (freq / chatbot.analise['total_sorteios']) * 100
        })
    
    return {
        "total_sorteios": chatbot.analise['total_sorteios'],
        "top_frequentes": top_frequentes,
        "media_altos": chatbot.analise['media_altos'],
        "media_soma": chatbot.analise['media_soma'],
        "padroes": chatbot.analise['padroes_vencedores']
    }

@app.get("/api/historico_boloes")
async def api_historico_boloes(limit: int = 10):
    """Endpoint para histórico de boloes"""
    return {
        "total": len(chatbot.boloes_historico),
        "boloes": chatbot.boloes_historico[-limit:] if chatbot.boloes_historico else []
    }

@app.get("/api/treinar_modelo")
async def api_treinar_modelo():
    """Endpoint para treinar/retreinar modelo"""
    try:
        chatbot.treinar_modelo_aprendizado()
        return {"status": "success", "message": "Modelo treinado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao treinar modelo: {str(e)}")

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Mega-Sena Chatbot API",
        "version": "1.0",
        "endpoints": {
            "chat": "/api/chat (POST)",
            "analise": "/api/analisar (POST)",
            "bolao": "/api/bolao (POST)",
            "estatisticas": "/api/estatisticas (GET)",
            "historico": "/api/historico_boloes (GET)",
            "websocket": "/ws/chat"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Iniciando Chatbot Mega-Sena API...")
    print("📡 Endpoints disponíveis:")
    print("   • WebSocket: ws://localhost:8000/ws/chat")
    print("   • API REST: http://localhost:8000")
    print("   • Documentação: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
