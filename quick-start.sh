#!/bin/bash

# Script de inicialização rápida do MegaSena AI

echo "🚀 INICIALIZAÇÃO RÁPIDA MEGA-SENA AI"
echo "====================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado!"
    echo "Instale Docker primeiro: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar arquivo CSV
if [ ! -f "resultados_megasena.csv" ]; then
    echo "📝 Criando arquivo CSV de exemplo..."
    cat > resultados_megasena.csv << CSV
n1,n2,n3,n4,n5,n6
4,5,30,33,41,52
10,12,19,35,39,49
6,17,18,19,44,58
1,3,33,35,44,58
5,7,10,11,30,33
2,18,20,25,32,58
3,4,39,41,42,50
5,10,23,30,48,59
2,17,23,31,38,59
3,16,18,35,45,51
CSV
    echo "✅ CSV criado com 10 sorteios exemplo"
fi

# Usar docker compose v2
echo "🚀 Iniciando serviços com Docker Compose..."
docker compose up -d

echo "⏳ Aguardando serviços iniciarem..."
sleep 15

# Verificar status
echo "📊 Status dos serviços:"
docker compose ps

echo ""
echo "✅ SISTEMA INICIADO COM SUCESSO!"
echo ""
echo "🌐 ACESSE:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8080"
echo "   IA Python: http://localhost:5001/docs"
echo ""
echo "🛠️  COMANDOS ÚTEIS:"
echo "   Ver logs: docker compose logs -f"
echo "   Parar:    docker compose down"
echo "   Status:   docker compose ps"
echo ""
echo "🎯 TESTE RÁPIDO:"
echo "   curl -X POST http://localhost:8080/api/generate \\"
echo '     -H "Content-Type: application/json" \'
echo '     -d '\''{"day": 15}'\'' | jq .games[0].numbers'
echo ""
echo "🎉 Pronto! Acesse http://localhost:3000 e comece a usar!"
