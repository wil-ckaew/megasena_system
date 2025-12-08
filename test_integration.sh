#!/bin/bash

echo "=========================================="
echo "🧪 TESTANDO INTEGRAÇÃO DO SISTEMA"
echo "=========================================="

# Parar containers existentes
echo "1. Parando containers existentes..."
docker-compose down

# Build dos serviços
echo "2. Fazendo build dos serviços..."
docker-compose build

# Iniciar serviços
echo "3. Iniciando todos os serviços..."
docker-compose up -d

# Aguardar inicialização
echo "4. Aguardando inicialização (30 segundos)..."
sleep 30

# Testar cada serviço
echo "5. Testando serviços..."

echo ""
echo "🔍 TESTANDO BACKEND RUST (porta 8080):"
curl -s http://localhost:8080/health || echo "❌ Backend não responde"

echo ""
echo "🤖 TESTANDO CHATBOT (porta 8000):"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ Chatbot não responde"

echo ""
echo "🧠 TESTANDO IA SERVICE (porta 5000):"
curl -s http://localhost:5000 || echo "❌ IA Service não responde"

echo ""
echo "🌐 TESTANDO FRONTEND (porta 3000):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 && echo "✅ Frontend responde" || echo "❌ Frontend não responde"

echo ""
echo "6. Testando API do Chatbot:"
echo "   Testando saudação..."
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá"}' | python3 -m json.tool

echo ""
echo "   Testando geração de jogo..."
curl -s -X POST http://localhost:8000/api/game \
  -H "Content-Type: application/json" \
  -d '{"quantity": 1}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    game = data['games'][0]
    print(f'✅ Jogo gerado: {game[\"numbers\"]}')
else:
    print('❌ Erro ao gerar jogo')
"

echo ""
echo "   Testando bolão..."
curl -s -X POST http://localhost:8000/api/bolao \
  -H "Content-Type: application/json" \
  -d '{"games": 3}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    print(f'✅ Bolão gerado com {data[\"games\"]} jogos')
    print(f'   Números únicos: {data[\"stats\"][\"unique_numbers\"]}/60')
else:
    print('❌ Erro ao gerar bolão')
"

echo ""
echo "=========================================="
echo "📊 RESUMO DOS SERVIÇOS:"
echo "=========================================="
echo "• Backend Rust:   http://localhost:8080"
echo "• Chatbot API:    http://localhost:8000"
echo "• IA Service:     http://localhost:5000"
echo "• Frontend:       http://localhost:3000"
echo ""
echo "📚 Documentação:"
echo "• Chatbot API:    http://localhost:8000/docs"
echo ""
echo "🎯 Para ver logs em tempo real:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar todos os serviços:"
echo "   docker-compose down"
echo "=========================================="
