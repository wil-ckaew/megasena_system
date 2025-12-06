#!/bin/bash

echo "🔄 Parando containers..."
docker stop megasena-frontend-container megasena-backend-container 2>/dev/null
docker rm megasena-frontend-container megasena-backend-container 2>/dev/null

echo "🚀 Iniciando backend..."
docker run -d -p 8080:8080 --name megasena-backend-container megasena-backend

sleep 3

echo "🧪 Testando backend..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Backend OK"
    echo "   Teste API:"
    curl -s -X POST http://localhost:8080/api/generate \
      -H "Content-Type: application/json" \
      -d '{"day":15}' | grep -o '"numbers":\[[^]]*\]'
else
    echo "❌ Backend falhou"
    docker logs megasena-backend-container --tail 5
    exit 1
fi

echo "⚛️ Iniciando frontend..."
docker run -d -p 3000:3000 --name megasena-frontend-container megasena-frontend

sleep 2

echo ""
echo "========================================"
echo "🎉 MEGA-SENA AI PRONTO!"
echo "========================================"
echo ""
echo "🌐 Acesse: http://localhost:3000"
echo ""
echo "📋 Como usar:"
echo "1. Escolha um dia (1-31)"
echo "2. Clique em GERAR"
echo "3. Use os números na sua aposta!"
echo ""
echo "🔧 Se der erro, abra o Console (F12) e me mostre!"
echo "========================================"
