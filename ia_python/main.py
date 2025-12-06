from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import random
import logging
import os
from contextlib import asynccontextmanager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class GenerateRequest(BaseModel):
    day: int = Field(ge=1, le=31, description="Dia do mês (1-31)")
    quantity: int = Field(default=1, ge=1, le=10, description="Quantidade de jogos a gerar")

class Game(BaseModel):
    numbers: List[int]
    sum: int
    high_numbers: int
    even_numbers: int
    method: str

class GenerateResponse(BaseModel):
    success: bool
    games: List[Game]
    day: int
    timestamp: str

# Classe principal da IA
class MegaSenaAI:
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or os.path.join(os.path.dirname(__file__), '../resultados_megasena.csv')
        self.data = None
        self.frequency = {}
        self.hot_numbers = []
        self.cold_numbers = []
        self.load_data()
    
    def load_data(self):
        """Carrega e analisa os dados históricos"""
        try:
            if os.path.exists(self.csv_path):
                self.data = pd.read_csv(self.csv_path)
                logger.info(f"Dados carregados: {len(self.data)} sorteios")
                self.analyze_data()
            else:
                logger.warning(f"Arquivo CSV não encontrado: {self.csv_path}")
                self.data = pd.DataFrame()
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            self.data = pd.DataFrame()
    
    def analyze_data(self):
        """Analisa dados históricos para encontrar padrões"""
        if self.data.empty:
            return
        
        # Coletar todos os números
        all_numbers = []
        for col in ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']:
            if col in self.data.columns:
                all_numbers.extend(self.data[col].tolist())
        
        # Calcular frequência
        from collections import Counter
        freq = Counter(all_numbers)
        self.frequency = dict(freq.most_common())
        
        # Identificar números quentes (mais frequentes)
        self.hot_numbers = [num for num, _ in freq.most_common(15)]
        
        # Identificar números frios (menos frequentes recentemente)
        self.cold_numbers = [num for num in range(1, 61) if num not in self.hot_numbers]
        
        logger.info(f"Análise concluída: {len(self.hot_numbers)} números quentes encontrados")
    
    def generate_game(self, day: int, method: str = "hybrid") -> List[int]:
        """Gera um jogo baseado no método especificado"""
        
        if method == "caravaca":
            return self.caravaca_method(day)
        elif method == "statistical":
            return self.statistical_method()
        elif method == "ai":
            return self.ai_method()
        else:  # hybrid
            return self.hybrid_method(day)
    
    def caravaca_method(self, day: int) -> List[int]:
        """Método Caravaca modificado com IA"""
        numbers = set()
        
        # Números baseados no dia
        base_numbers = [
            (day % 30) + 1,
            (day * 2 % 60) + 1,
            (day * 3 % 60) + 1,
            (day * 5 % 60) + 1,
        ]
        
        numbers.update([n for n in base_numbers if 1 <= n <= 60])
        
        # Adicionar números quentes
        for hot_num in self.hot_numbers:
            if len(numbers) >= 6:
                break
            if hot_num not in numbers:
                numbers.add(hot_num)
        
        # Completar com números aleatórios balanceados
        while len(numbers) < 6:
            num = random.randint(1, 60)
            if num not in numbers:
                numbers.add(num)
        
        return sorted(list(numbers))
    
    def statistical_method(self) -> List[int]:
        """Método puramente estatístico"""
        numbers = set()
        
        # Escolher 2 números quentes
        hot_selected = random.sample(self.hot_numbers[:10], 2)
        numbers.update(hot_selected)
        
        # Escolher 2 números frios
        cold_selected = random.sample(self.cold_numbers[:20], 2)
        numbers.update(cold_selected)
        
        # Escolher 2 números aleatórios
        while len(numbers) < 6:
            num = random.randint(1, 60)
            if num not in numbers:
                numbers.add(num)
        
        return sorted(list(numbers))
    
    def ai_method(self) -> List[int]:
        """Método de machine learning simples"""
        numbers = set()
        
        # Simular modelo de ML (em produção seria um modelo treinado)
        # Usar distribuição baseada na frequência
        probs = [self.frequency.get(i, 0.1) for i in range(1, 61)]
        total = sum(probs)
        probs = [p/total for p in probs]
        
        # Amostrar números baseado nas probabilidades
        ai_numbers = np.random.choice(range(1, 61), size=8, p=probs, replace=False)
        numbers.update(ai_numbers[:6])
        
        return sorted(list(numbers))
    
    def hybrid_method(self, day: int) -> List[int]:
        """Método híbrido: Caravaca + Estatística + IA"""
        numbers = set()
        
        # 1. Dois números do método Caravaca
        caravaca_nums = self.caravaca_method(day)
        numbers.update(caravaca_nums[:2])
        
        # 2. Dois números estatísticos
        stat_nums = self.statistical_method()
        numbers.update(stat_nums[:2])
        
        # 3. Dois números da IA
        ai_nums = self.ai_method()
        
        # Garantir 6 números únicos
        all_candidates = list(set(caravaca_nums + stat_nums + ai_nums))
        if len(all_candidates) >= 6:
            numbers = set(random.sample(all_candidates, 6))
        else:
            while len(numbers) < 6:
                numbers.add(random.randint(1, 60))
        
        return sorted(list(numbers))
    
    def generate_games(self, day: int, quantity: int = 1) -> List[List[int]]:
        """Gera múltiplos jogos"""
        games = []
        for i in range(quantity):
            method = random.choice(["hybrid", "caravaca", "statistical", "ai"])
            game = self.generate_game(day, method)
            games.append(game)
        return games

# Inicializar IA
ai = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização
    global ai
    ai = MegaSenaAI()
    logger.info("✅ IA Python inicializada")
    yield
    # Cleanup
    logger.info("🛑 IA Python finalizada")

# Criar app FastAPI
app = FastAPI(
    title="MegaSena AI API",
    description="API de Machine Learning para geração de jogos da Mega-Sena",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "MegaSena AI Python",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate": "/api/generate",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health():
    global ai
    return {
        "status": "healthy" if ai else "initializing",
        "service": "MegaSena AI Python",
        "data_loaded": ai.data is not None and not ai.data.empty,
        "hot_numbers_count": len(ai.hot_numbers) if ai else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    try:
        if not ai:
            raise HTTPException(status_code=503, detail="IA não inicializada")
        
        logger.info(f"Gerando {request.quantity} jogo(s) para dia {request.day}")
        
        games_data = []
        all_games = ai.generate_games(request.day, request.quantity)
        
        for game_numbers in all_games:
            # Calcular estatísticas
            game_sum = sum(game_numbers)
            high_count = len([n for n in game_numbers if n >= 35])
            even_count = len([n for n in game_numbers if n % 2 == 0])
            
            games_data.append(Game(
                numbers=game_numbers,
                sum=game_sum,
                high_numbers=high_count,
                even_numbers=even_count,
                method="hybrid_ai"
            ))
        
        return GenerateResponse(
            success=True,
            games=games_data,
            day=request.day,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar jogos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis")
async def get_analysis():
    """Retorna análise dos dados históricos"""
    if not ai or ai.data.empty:
        raise HTTPException(status_code=503, detail="Dados não carregados")
    
    return {
        "total_games": len(ai.data),
        "hot_numbers": ai.hot_numbers[:10],
        "frequency": ai.frequency,
        "analysis_timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )
