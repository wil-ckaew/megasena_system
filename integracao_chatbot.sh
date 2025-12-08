#!/bin/bash

echo "=========================================="
echo "🚀 INTEGRAÇÃO CHATBOT + BOLÃO MEGA-SENA"
echo "=========================================="

# 1. Verificar dependências
echo "1. Verificando dependências..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi

# 2. Instalar dependências Python
echo "2. Instalando dependências Python..."
pip install fastapi uvicorn scikit-learn pandas numpy

# 3. Verificar arquivo CSV
echo "3. Verificando dados históricos..."
if [ ! -f "resultados_megasena.csv" ]; then
    echo "❌ Arquivo resultados_megasena.csv não encontrado!"
    echo "📁 Criando arquivo de exemplo..."
    cat > resultados_megasena.csv << 'CSVEOF'
Concurso,Data,n1,n2,n3,n4,n5,n6
2933,28/10/2025,1,18,22,42,48,50
2932,25/10/2025,4,13,25,36,40,53
2931,23/10/2025,4,19,23,36,47,52
2930,21/10/2025,1,11,13,14,36,45
CSVEOF
fi

# 4. Criar arquivos necessários
echo "4. Criando arquivos de suporte..."
touch boloes_historico.json
echo '[]' > boloes_historico.json

# 5. Iniciar serviços
echo "5. Iniciando serviços..."
echo ""
echo "🎯 OPÇÕES DE INICIALIZAÇÃO:"
echo "   1. Chatbot API apenas"
echo "   2. Chatbot + Frontend Next.js"
echo "   3. Todos serviços (Docker Compose)"
echo "   4. Testar integração"
echo ""

read -p "👉 Escolha uma opção (1-4): " opcao

case $opcao in
    1)
        echo "🚀 Iniciando Chatbot API..."
        cd ml_service
        python chatbot_service.py
        ;;
    2)
        echo "🚀 Iniciando Chatbot + Frontend..."
        
        # Iniciar chatbot em background
        cd ml_service
        python chatbot_service.py &
        CHATBOT_PID=$!
        
        # Iniciar frontend
        cd ../frontend_nextjs
        npm run dev &
        FRONTEND_PID=$!
        
        echo "✅ Serviços iniciados!"
        echo "   • Chatbot: http://localhost:8000"
        echo "   • Frontend: http://localhost:3000"
        echo "   • Documentação: http://localhost:8000/docs"
        
        # Esperar Ctrl+C
        wait $CHATBOT_PID $FRONTEND_PID
        ;;
    3)
        echo "🐳 Iniciando com Docker Compose..."
        if [ -f "docker-compose.chatbot.yml" ]; then
            docker-compose -f docker-compose.chatbot.yml up --build
        else
            echo "❌ Arquivo docker-compose.chatbot.yml não encontrado!"
        fi
        ;;
    4)
        echo "🧪 Testando integração..."
        
        # Testar chatbot
        echo "Testando Chatbot API..."
        curl -X POST http://localhost:8000/api/chat \
            -H "Content-Type: application/json" \
            -d '{"text": "Olá", "user_id": "teste"}' \
            --max-time 10 \
            || echo "❌ Chatbot não está respondendo"
        
        # Testar geração de bolão
        echo "Testando geração de bolão..."
        curl -X POST http://localhost:8000/api/bolao \
            -H "Content-Type: application/json" \
            -d '{"quantidade_jogos": 3, "metodo": "optimized"}' \
            --max-time 10 \
            || echo "❌ API de bolão não está respondendo"
        
        echo "✅ Testes concluídos!"
        ;;
    *)
        echo "❌ Opção inválida!"
        ;;
esac

echo ""
echo "=========================================="
echo "🤖 SISTEMA PRONTO PARA USO!"
echo "=========================================="
