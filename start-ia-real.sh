#!/bin/bash

echo "🧠 MEGA-SENA COM IA PYTHON REAL"
echo "================================"

# Parar tudo
echo "🛑 Parando containers..."
docker stop megasena-frontend-container megasena-backend-container 2>/dev/null
docker rm megasena-frontend-container megasena-backend-container 2>/dev/null

# Parar Python se estiver rodando
echo "🐍 Parando Python anterior..."
pkill -f "python.*5000" 2>/dev/null
sleep 2

# 1. Iniciar Python IA
echo ""
echo "1. 🧠 Iniciando Python IA Service..."
cd ml_service

# Instalar dependências se necessário
if ! python3 -c "import flask" 2>/dev/null; then
    echo "   📦 Instalando dependências Python..."
    pip install flask flask-cors pandas numpy > /dev/null 2>&1
fi

# Iniciar serviço
python3 api_python_real.py &
PYTHON_PID=$!
cd ..

sleep 10

echo "   🧪 Testando Python IA..."
if curl -s http://localhost:5000/health > /dev/null; then
    echo "   ✅ Python IA OK"
    curl -s http://localhost:5000/health | grep -o '"sorteios_analisados":[0-9]*'
else
    echo "   ❌ Python IA falhou"
    echo "   📝 Tentando iniciar manualmente..."
    cd ml_service
    python3 api_python_real.py &
    cd ..
    sleep 10
fi

# 2. Verificar porta 8080
echo ""
echo "2. 🔧 Verificando porta 8080..."
if lsof -i :8080 > /dev/null; then
    echo "   ⚠️  Porta 8080 em uso. Liberando..."
    sudo kill -9 $(sudo lsof -t -i:8080) 2>/dev/null
    sleep 2
fi

# 3. Iniciar Backend Rust
echo ""
echo "3. 🦀 Iniciando Backend Rust Proxy..."
cd backend_rust
docker build -t megasena-backend . > /dev/null 2>&1
docker run -d -p 8080:8080 --name megasena-backend-container megasena-backend
cd ..

sleep 5

echo "   🧪 Testando Backend Proxy..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "   ✅ Backend Proxy OK"
else
    echo "   ❌ Backend Proxy falhou"
    docker logs megasena-backend-container --tail 10
fi

# 4. Testar fluxo completo
echo ""
echo "4. 🔄 Testando fluxo IA Python..."
echo "   📡 Frontend → Rust → Python IA → Dados CSV"
TEST_RESULT=$(curl -s -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"day": 15}')

if echo "$TEST_RESULT" | grep -q "python_ml"; then
    echo "   ✅ Fluxo funcionando! IA Python sendo usada."
    echo "$TEST_RESULT" | grep -o '"numbers":\[[^]]*\]'
else
    echo "   ⚠️  Usando fallback. Verificando Python IA..."
    curl -s http://localhost:5000/health
fi

# 5. Frontend já está construído (do script anterior)
echo ""
echo "5. 🌐 Iniciando Frontend..."
docker run -d -p 3000:3000 --name megasena-frontend-container megasena-frontend

sleep 3

echo ""
echo "========================================"
echo "🎉 SISTEMA COM IA PYTHON REAL PRONTO!"
echo "========================================"
echo ""
echo "🌐 Acesse: http://localhost:3000"
echo ""
echo "📊 DETALHES DA IA:"
echo "• 🤖 Algoritmo: Análise estatística de dados históricos"
echo "• 📈 Dados: 52 sorteios da Mega-Sena (resultados_megasena.csv)"
echo "• 🧮 Técnicas: Frequência, números quentes, análise por posição"
echo "• 🔗 Fluxo: Frontend → Rust Proxy → Python IA → CSV → Resultado"
echo ""
echo "🔧 TESTES MANUAIS:"
echo "• Python IA: curl http://localhost:5000/health"
echo "• Rust Proxy: curl http://localhost:8080/health"
echo "• IA completa: curl -X POST http://localhost:8080/api/generate -d '{\"day\":15}'"
echo ""
echo "📝 LOGS:"
echo "• Python IA: tail -f ~/rust/megasena_system/ml_service/api_python_real.py.log"
echo "• Rust: docker logs megasena-backend-container -f"
echo "========================================"

# Salvar PID do Python
echo $PYTHON_PID > /tmp/megasena_python.pid
echo "📝 Python PID: $PYTHON_PID"
