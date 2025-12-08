#!/usr/bin/env python3
"""
🤖 CHATBOT MEGA-SENA - VERSÃO SIMPLES
API básica para integração com seu sistema
"""

import pandas as pd
import numpy as np
import random
import json
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(title="Mega-Sena Chatbot API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class GameRequest(BaseModel):
    quantity: int = 1
    include_high: bool = True

class GameAnalysis(BaseModel):
    numbers: List[int]

class BolaoRequest(BaseModel):
    games: int = 10
    include_stats: bool = True

# Classe do Chatbot
class MegaSenaChatbot:
    def __init__(self):
        self.csv_path = 'resultados_megasena.csv'
        self.df = None
        self.analysis = {}
        self.load_data()
    
    def load_data(self):
        """Carrega dados históricos"""
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path)
                print(f"✅ Dados carregados: {len(self.df)} sorteios")
                
                # Detectar colunas
                if 'n1' in self.df.columns:
                    self.number_cols = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']
                elif 'bola 1' in self.df.columns:
                    self.number_cols = ['bola 1', 'bola 2', 'bola 3', 'bola 4', 'bola 5', 'bola 6']
                else:
                    # Encontrar colunas numéricas
                    numeric_cols = []
                    for col in self.df.columns:
                        try:
                            if pd.api.types.is_numeric_dtype(self.df[col]):
                                numeric_cols.append(col)
                        except:
                            continue
                    self.number_cols = numeric_cols[:6]
                
                print(f"📊 Colunas de números: {self.number_cols}")
                self.analyze_data()
                
        except Exception as e:
            print(f"⚠️  Erro ao carregar dados: {e}")
            self.df = None
    
    def analyze_data(self):
        """Analisa dados históricos"""
        if self.df is None or len(self.number_cols) < 6:
            return
        
        from collections import Counter
        frequencies = Counter()
        
        for col in self.number_cols:
            if col in self.df.columns:
                frequencies.update(self.df[col].dropna().astype(int).values)
        
        # Calcular números altos por jogo
        high_counts = []
        for _, row in self.df.iterrows():
            game = [row[col] for col in self.number_cols if col in self.df.columns]
            highs = sum(1 for n in game if n >= 35)
            high_counts.append(highs)
        
        self.analysis = {
            'frequencies': frequencies,
            'total_games': len(self.df),
            'avg_highs': np.mean(high_counts) if high_counts else 2.5,
            'avg_sum': 210  # Valor padrão
        }
        
        print(f"📈 Análise: {self.analysis['total_games']} jogos, média de altos: {self.analysis['avg_highs']:.2f}")
    
    def generate_optimized_game(self):
        """Gera jogo otimizado"""
        # Usar análise real se disponível
        if self.analysis and 'avg_highs' in self.analysis:
            n_highs = int(round(self.analysis['avg_highs']))
            n_highs = max(1, min(4, n_highs))  # Entre 1 e 4
        else:
            n_highs = random.randint(2, 3)
        
        n_lows = 6 - n_highs
        
        # Garantir números únicos
        while True:
            try:
                highs = sorted(random.sample(range(35, 61), n_highs))
                lows = sorted(random.sample(range(1, 35), n_lows))
                game = sorted(lows + highs)
                
                # Verificar se são únicos
                if len(set(game)) == 6:
                    return game
            except ValueError:
                # Se não conseguir amostra suficiente, ajustar
                n_highs = max(1, min(4, n_highs - 1))
                n_lows = 6 - n_highs
    
    def generate_bolao(self, num_games):
        """Gera bolão com múltiplos jogos"""
        bolao = []
        all_numbers = set()
        
        for _ in range(num_games):
            game = self.generate_optimized_game()
            bolao.append(game)
            all_numbers.update(game)
        
        return {
            'games': bolao,
            'unique_numbers': len(all_numbers),
            'coverage': len(all_numbers) / 60,
            'avg_highs': np.mean([sum(1 for n in g if n >= 35) for g in bolao])
        }
    
    def analyze_game(self, numbers):
        """Analisa um jogo específico"""
        game = sorted(numbers[:6])
        
        return {
            'sum': sum(game),
            'highs': sum(1 for n in game if n >= 35),
            'lows': sum(1 for n in game if n <= 20),
            'evens': sum(1 for n in game if n % 2 == 0),
            'odds': 6 - sum(1 for n in game if n % 2 == 0)
        }
    
    def process_message(self, message):
        """Processa mensagem do usuário"""
        message = message.lower().strip()
        
        # Saudação
        if any(word in message for word in ['oi', 'olá', 'hello', 'bom dia', 'boa tarde']):
            return {
                "response": "Olá! Sou o chatbot da Mega-Sena 🤖\n\nPosso ajudar com:\n🎯 Geração de jogos otimizados\n🏆 Criação de boloes\n📊 Análise de seus números\n📈 Estatísticas históricas\n\nO que gostaria de fazer?",
                "type": "greeting",
                "suggestions": ["Gerar jogo", "Criar bolão", "Ver estatísticas", "Analisar números"]
            }
        
        # Gerar jogo
        elif any(word in message for word in ['gerar', 'jogo', 'número', 'numero', 'sugerir']):
            game = self.generate_optimized_game()
            stats = self.analyze_game(game)
            
            return {
                "response": f"🎲 **Jogo otimizado gerado:**\n`{', '.join(f'{n:2d}' for n in game)}`\n\n📊 **Estatísticas:**\n• Soma: {stats['sum']}\n• Números altos (≥35): {stats['highs']}\n• Pares/Ímpares: {stats['evens']}/{stats['odds']}",
                "type": "game",
                "game": game,
                "stats": stats
            }
        
        # Bolão
        elif any(word in message for word in ['bolão', 'bolao', 'vários', 'múltiplos', 'grupo']):
            # Extrair quantidade
            numbers = re.findall(r'\d+', message)
            quantity = int(numbers[0]) if numbers else 5
            quantity = min(max(1, quantity), 20)  # Limitar a 20 jogos
            
            bolao = self.generate_bolao(quantity)
            
            response = f"🏆 **Bolão de {quantity} jogos gerado!**\n\n"
            response += f"📊 **Estatísticas:**\n"
            response += f"• Números únicos cobertos: {bolao['unique_numbers']}/60\n"
            response += f"• Cobertura: {bolao['coverage']:.1%}\n"
            response += f"• Média de altos por jogo: {bolao['avg_highs']:.1f}\n\n"
            
            response += "🎲 **Primeiros jogos:**\n"
            for i, game in enumerate(bolao['games'][:3], 1):
                stats = self.analyze_game(game)
                response += f"{i}. `{', '.join(f'{n:2d}' for n in game)}` "
                response += f"(Soma: {stats['sum']}, Altos: {stats['highs']})\n"
            
            if quantity > 3:
                response += f"\n... e mais {quantity - 3} jogos otimizados"
            
            return {
                "response": response,
                "type": "bolao",
                "bolao": bolao['games'],
                "stats": bolao
            }
        
        # Estatísticas
        elif any(word in message for word in ['estatística', 'estatisticas', 'frequente', 'atrasado']):
            if not self.analysis:
                return {
                    "response": "❌ Dados históricos não disponíveis no momento.",
                    "type": "error"
                }
            
            response = "📊 **Estatísticas Históricas**\n\n"
            response += f"• Total de sorteios analisados: {self.analysis['total_games']}\n"
            response += f"• Média de números altos (≥35) por jogo: {self.analysis['avg_highs']:.2f}\n"
            response += f"• Soma média dos jogos: ~210\n\n"
            
            response += "🎯 **Números mais frequentes (Top 5):**\n"
            for num, freq in self.analysis['frequencies'].most_common(5):
                percentage = (freq / self.analysis['total_games']) * 100
                response += f"• Nº {num:2d}: {freq:3d} vezes ({percentage:.1f}%)\n"
            
            return {
                "response": response,
                "type": "stats"
            }
        
        # Análise
        elif any(word in message for word in ['analisar', 'checar', 'verificar', 'meu jogo']):
            # Extrair números
            numbers = re.findall(r'\b\d{1,2}\b', message)
            numbers = [int(n) for n in numbers if 1 <= int(n) <= 60]
            
            if len(numbers) < 6:
                return {
                    "response": "❌ Preciso de 6 números entre 1 e 60 para analisar.\nExemplo: 'Analisar 10 20 30 40 50 60'",
                    "type": "error"
                }
            
            game = sorted(numbers[:6])
            stats = self.analyze_game(game)
            
            response = f"🔍 **Análise do seu jogo:**\n`{', '.join(f'{n:2d}' for n in game)}`\n\n"
            response += f"📊 **Estatísticas:**\n"
            response += f"• Soma total: {stats['sum']}\n"
            response += f"• Números altos (≥35): {stats['highs']}\n"
            response += f"• Números baixos (≤20): {stats['lows']}\n"
            response += f"• Pares/Ímpares: {stats['evens']}/{stats['odds']}\n\n"
            
            response += "💡 **Recomendações:**\n"
            
            recommendations = []
            if stats['highs'] == 0:
                recommendations.append("Adicione 1-2 números altos (≥35)")
            elif stats['highs'] > 3:
                recommendations.append("Considere reduzir números altos (ideal 2-3)")
            
            if stats['lows'] == 0:
                recommendations.append("Adicione 1-2 números baixos (≤20)")
            
            if stats['evens'] < 2 or stats['evens'] > 4:
                recommendations.append("Balanceie pares/ímpares (ideal 2-4 de cada)")
            
            if stats['sum'] < 180 or stats['sum'] > 240:
                recommendations.append(f"Soma ({stats['sum']}) fora da faixa ideal (180-240)")
            
            if not recommendations:
                recommendations.append("Seu jogo está bem balanceado! Boa sorte! 🍀")
            
            for i, rec in enumerate(recommendations, 1):
                response += f"{i}. {rec}\n"
            
            return {
                "response": response,
                "type": "analysis",
                "game": game,
                "stats": stats,
                "recommendations": recommendations
            }
        
        # Ajuda
        elif any(word in message for word in ['ajuda', 'help', 'como usar', 'o que faz']):
            return {
                "response": "🎰 **COMO USAR O CHATBOT:**\n\n"
                          "• **Gerar jogo:** 'Gerar números', 'Sugerir jogo'\n"
                          "• **Criar bolão:** 'Gerar bolão', '10 jogos'\n"
                          "• **Estatísticas:** 'Mostrar estatísticas', 'Números frequentes'\n"
                          "• **Analisar:** 'Analisar 10 20 30 40 50 60'\n"
                          "• **Dicas:** 'Dicas para apostar'\n\n"
                          "💬 Basta digitar o que precisa!",
                "type": "help"
            }
        
        # Dicas
        elif any(word in message for word in ['dica', 'conselho', 'estratégia', 'como ganhar']):
            tips = [
                "🎯 **Misture números altos (35-60) e baixos (1-34)**",
                "🎯 **Use 2-4 números pares e 2-4 ímpares**",
                "🎯 **A soma ideal fica entre 180-240**",
                "🎯 **Evite sequências (ex: 1,2,3,4,5,6)**",
                "🎯 **Considere números que estão atrasados**",
                "🎯 **Não use apenas datas de aniversário**",
                "🎯 **Em bolões, maximize a cobertura de números diferentes**",
                "🎯 **Aposte com responsabilidade!**"
            ]
            
            return {
                "response": "💡 **DICAS ESTRATÉGICAS:**\n\n" + "\n".join(tips),
                "type": "tips"
            }
        
        # Resposta padrão
        else:
            return {
                "response": "🤔 Não entendi completamente. Posso ajudar com:\n"
                          "• Geração de jogos otimizados\n"
                          "• Criação de boloes\n"
                          "• Análise de números\n"
                          "• Estatísticas históricas\n\n"
                          "Tente perguntar de outra forma!",
                "type": "default"
            }

# Instanciar chatbot
chatbot = MegaSenaChatbot()

# Endpoints da API
@app.get("/")
async def root():
    return {
        "service": "Mega-Sena Chatbot API",
        "version": "1.0",
        "status": "online",
        "endpoints": {
            "chat": "POST /api/chat",
            "game": "POST /api/game",
            "bolao": "POST /api/bolao",
            "analyze": "POST /api/analyze",
            "stats": "GET /api/stats",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": chatbot.df is not None
    }

@app.get("/api/stats")
async def get_stats():
    if not chatbot.analysis:
        raise HTTPException(status_code=503, detail="Dados não disponíveis")
    
    # Preparar dados para frontend
    top_numbers = []
    for num, freq in chatbot.analysis['frequencies'].most_common(10):
        top_numbers.append({
            "number": num,
            "frequency": freq,
            "percentage": (freq / chatbot.analysis['total_games']) * 100
        })
    
    return {
        "total_games": chatbot.analysis['total_games'],
        "avg_highs": chatbot.analysis['avg_highs'],
        "avg_sum": chatbot.analysis['avg_sum'],
        "top_numbers": top_numbers
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = chatbot.process_message(request.message)
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")

@app.post("/api/game")
async def generate_game(request: GameRequest):
    try:
        games = []
        for _ in range(request.quantity):
            game = chatbot.generate_optimized_game()
            stats = chatbot.analyze_game(game)
            games.append({
                "numbers": game,
                "stats": stats
            })
        
        return {
            "success": True,
            "quantity": request.quantity,
            "games": games
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar jogo: {str(e)}")

@app.post("/api/bolao")
async def generate_bolao(request: BolaoRequest):
    try:
        bolao_data = chatbot.generate_bolao(request.games)
        
        response = {
            "success": True,
            "games": request.games,
            "bolao": bolao_data['games'],
            "stats": {
                "unique_numbers": bolao_data['unique_numbers'],
                "coverage": bolao_data['coverage'],
                "avg_highs": bolao_data['avg_highs']
            }
        }
        
        if request.include_stats:
            # Calcular estatísticas detalhadas
            all_games_stats = [chatbot.analyze_game(g) for g in bolao_data['games']]
            response["detailed_stats"] = all_games_stats
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar bolão: {str(e)}")

@app.post("/api/analyze")
async def analyze_game(request: GameAnalysis):
    try:
        if len(request.numbers) < 6:
            raise HTTPException(status_code=400, detail="Forneça pelo menos 6 números")
        
        stats = chatbot.analyze_game(request.numbers)
        
        # Recomendações
        recommendations = []
        if stats['highs'] == 0:
            recommendations.append("Adicione 1-2 números altos (≥35)")
        elif stats['highs'] > 3:
            recommendations.append("Considere reduzir números altos (ideal 2-3)")
        
        if stats['lows'] == 0:
            recommendations.append("Adicione 1-2 números baixos (≤20)")
        
        if stats['evens'] < 2 or stats['evens'] > 4:
            recommendations.append("Balanceie pares/ímpares (ideal 2-4 de cada)")
        
        if stats['sum'] < 180 or stats['sum'] > 240:
            recommendations.append(f"Soma ({stats['sum']}) fora da faixa ideal (180-240)")
        
        return {
            "success": True,
            "game": request.numbers[:6],
            "stats": stats,
            "recommendations": recommendations,
            "balanced": len(recommendations) == 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar jogo: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🤖 Chatbot Mega-Sena iniciando...")
    print("📡 Endpoint: http://0.0.0.0:8000")
    print("📊 Dados carregados:", "✅" if chatbot.df is not None else "❌")
    uvicorn.run(app, host="0.0.0.0", port=8000)
