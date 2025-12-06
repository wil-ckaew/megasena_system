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
else
    echo "❌ Backend falhou"
    exit 1
fi

echo "⚛️ Iniciando frontend..."
docker run -d -p 3000:3000 --name megasena-frontend-container megasena-frontend

sleep 2

echo ""
echo "========================================"
echo "🎉 SISTEMA PRONTO!"
echo "========================================"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8080"
echo "📊 Health:   http://localhost:8080/health"
echo ""
echo "🎯 Instruções:"
echo "1. Abra http://localhost:3000"
echo "2. Escolha um dia (1-31)"
echo "3. Clique em GERAR"
echo "4. Use os números na sua aposta!"
echo "========================================"
