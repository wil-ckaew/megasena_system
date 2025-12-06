#!/bin/bash

echo "🎰 MEGA-SENA AI - SISTEMA COMPLETO"
echo "=================================="

# Parar tudo
echo "🛑 Parando todos os containers..."
docker stop megasena-frontend-container megasena-backend-container megasena-ml-container 2>/dev/null
docker rm megasena-frontend-container megasena-backend-container megasena-ml-container 2>/dev/null

# 1. Iniciar Python ML Service
echo ""
echo "1. 🐍 Iniciando Python ML Service (porta 5000)..."
cd ml_service
docker build -t megasena-ml-service . 2>&1 | tail -5
docker run -d \
  -p 5000:5000 \
  --name megasena-ml-container \
  megasena-ml-service
cd ..

sleep 5
echo "   ⏳ Aguardando serviço Python..."

# Testar Python ML
echo "   🧪 Testando Python ML Service..."
if curl -s http://localhost:5000/health > /dev/null; then
    echo "   ✅ Python ML Service OK"
else
    echo "   ⚠️  Python ML pode estar iniciando ainda..."
fi

# 2. Iniciar Backend Rust
echo ""
echo "2. 🦀 Iniciando Backend Rust (porta 8080)..."
cd backend_rust
docker build -t megasena-backend . 2>&1 | tail -5
docker run -d \
  -p 8080:8080 \
  --name megasena-backend-container \
  megasena-backend
cd ..

sleep 3

# Testar Rust Backend
echo "   🧪 Testando Backend Rust..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "   ✅ Rust Backend OK"
else
    echo "   ❌ Rust Backend falhou"
    docker logs megasena-backend-container --tail 5
fi

# 3. Iniciar Frontend
echo ""
echo "3. ⚛️ Iniciando Frontend React (porta 3000)..."
cd frontend_nextjs
docker build -t megasena-frontend . 2>&1 | tail -5
docker run -d \
  -p 3000:3000 \
  --name megasena-frontend-container \
  megasena-frontend
cd ..

sleep 3

echo ""
echo "========================================"
echo "🎉 SISTEMA COMPLETO PRONTO!"
echo "========================================"
echo ""
echo "🌐 URLs PARA ACESSO:"
echo "• Frontend:       http://localhost:3000"
echo "• Rust Backend:   http://localhost:8080"
echo "• Python ML:      http://localhost:5000"
echo ""
echo "🔧 ENDPOINTS:"
echo "• Rust Health:    http://localhost:8080/health"
echo "• Python Health:  http://localhost:5000/health"
echo "• API Generate:   http://localhost:8080/api/generate"
echo ""
echo "🎯 MÉTODOS DISPONÍVEIS:"
echo "1. 🦀 Rust - Algoritmo determinístico rápido"
echo "2. 🐍 Python - IA com análise de 52 sorteios"
echo "3. 🔗 Híbrido - Combinação inteligente"
echo ""
echo "📊 DADOS:"
echo "• Sorteios analisados: 52"
echo "• CSV: resultados_megasena.csv"
echo "• Algoritmo: Random Forest + Estatística"
echo ""
echo "💡 COMO USAR:"
echo "1. Acesse http://localhost:3000"
echo "2. Escolha o método de geração"
echo "3. Selecione o dia (1-31)"
echo "4. Clique em GERAR JOGO"
echo "5. Use os números na sua aposta!"
echo "========================================"

# Mostrar logs
echo ""
echo "📝 LOGS DOS SERVIÇOS (últimas 5 linhas):"
echo "----------------------------------------"
echo "Python ML:"
docker logs megasena-ml-container --tail 5 2>/dev/null || echo "Container não encontrado"
echo ""
echo "Rust Backend:"
docker logs megasena-backend-container --tail 5 2>/dev/null || echo "Container não encontrado"
echo ""
echo "Para ver logs completos:"
echo "• Python: docker logs megasena-ml-container -f"
echo "• Rust:   docker logs megasena-backend-container -f"
echo "• Front:  docker logs megasena-frontend-container -f"
