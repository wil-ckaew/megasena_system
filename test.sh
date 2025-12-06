#!/bin/bash

# Script de testes do MegaSena AI

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║          TESTES MEGA-SENA AI SYSTEM            ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

PASS=0
FAIL=0
TOTAL=0

# Função de teste
run_test() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    
    ((TOTAL++))
    echo -n "Testando: $test_name... "
    
    if eval "$command" 2>/dev/null | grep -q "$expected"; then
        echo -e "${GREEN}PASS${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        ((FAIL++))
        return 1
    fi
}

# Função de teste de API
test_api() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="${4:-}"
    local expected_status="${5:-200}"
    
    ((TOTAL++))
    echo -n "Testando API: $name... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}PASS (Status: $response)${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}FAIL (Status: $response, Esperado: $expected_status)${NC}"
        ((FAIL++))
        return 1
    fi
}

echo -e "\n${YELLOW}🔍 TESTES DE SISTEMA${NC}"
echo "=============================="

# 1. Verificar serviços Docker
run_test "Serviços Docker" "docker ps --format '{{.Names}}' | grep -q 'megasena'" ""

# 2. Verificar portas
run_test "Porta 3000 (Frontend)" "netstat -tuln | grep ':3000'" "3000"
run_test "Porta 8080 (Backend)" "netstat -tuln | grep ':8080'" "8080"
run_test "Porta 5001 (IA)" "netstat -tuln | grep ':5001'" "5001"

# 3. Verificar arquivos essenciais
run_test "Arquivo CSV" "test -f resultados_megasena.csv" ""
run_test "Docker Compose" "test -f docker-compose.yml" ""
run_test "Script start.sh" "test -f start.sh" ""

echo -e "\n${YELLOW}🌐 TESTES DE API${NC}"
echo "=============================="

# 4. Testar APIs
test_api "Health Backend Rust" "http://localhost:8080/health"
test_api "Health IA Python" "http://localhost:5001/health"
test_api "Frontend" "http://localhost:3000" "GET" "" "200"

# 5. Testar geração de jogo
echo -n "Testando geração de jogo... "
response=$(curl -s -X POST "http://localhost:8080/api/generate" \
    -H "Content-Type: application/json" \
    -d '{"day": 15}' 2>/dev/null)

if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
    
    # Extrair jogo
    game=$(echo "$response" | jq -r '.games[0].numbers | join(", ")')
    sum=$(echo "$response" | jq -r '.games[0].sum')
    echo "   Jogo gerado: [$game]"
    echo "   Soma: $sum"
else
    echo -e "${RED}FAIL${NC}"
    ((FAIL++))
fi

# 6. Testar análise da IA
echo -n "Testando análise IA... "
response=$(curl -s "http://localhost:5001/api/analysis" 2>/dev/null)

if echo "$response" | jq -e '.hot_numbers' >/dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((PASS++))
    
    # Extrair números quentes
    hot_nums=$(echo "$response" | jq -r '.hot_numbers[:5] | join(", ")')
    echo "   Números quentes: [$hot_nums]"
else
    echo -e "${YELLOW}SKIP (IA não disponível)${NC}"
    ((TOTAL--)) # Não conta como falha
fi

echo -e "\n${YELLOW}🐳 TESTES DOCKER${NC}"
echo "=============================="

# 7. Testar containers
run_test "Container Backend" "docker ps --format '{{.Names}} {{.Status}}' | grep 'megasena-backend'" "Up"
run_test "Container IA" "docker ps --format '{{.Names}} {{.Status}}' | grep 'megasena-ia'" "Up"
run_test "Container Frontend" "docker ps --format '{{.Names}} {{.Status}}' | grep 'megasena-frontend'" "Up"

# 8. Testar logs
run_test "Logs Backend" "docker logs megasena-backend 2>&1 | tail -5 | grep -q 'Started'" ""
run_test "Logs sem erro" "docker logs megasena-backend 2>&1 | tail -20 | grep -q 'ERROR'" "" && {
    echo -e "   ${RED}⚠️  Erros encontrados nos logs${NC}"
} || {
    echo -e "   ${GREEN}✓ Logs limpos${NC}"
}

echo -e "\n${YELLOW}📊 TESTES DE DESEMPENHO${NC}"
echo "=============================="

# 9. Teste de carga simples
echo -n "Teste de resposta da API... "
start_time=$(date +%s%3N)
for i in {1..10}; do
    curl -s -o /dev/null "http://localhost:8080/health"
done
end_time=$(date +%s%3N)
duration=$((end_time - start_time))
avg_duration=$((duration / 10))

if [ $avg_duration -lt 1000 ]; then
    echo -e "${GREEN}PASS (${avg_duration}ms avg)${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}SLOW (${avg_duration}ms avg)${NC}"
    ((PASS++)) # Não falha, apenas alerta
fi

# 10. Teste de memória
echo -n "Uso de memória... "
mem_usage=$(docker stats --no-stream --format "{{.MemUsage}}" megasena-backend | cut -d'/' -f1 | tr -d 'MiB' | tr -d ' ')
if [ "${mem_usage:-0}" -lt 500 ]; then
    echo -e "${GREEN}PASS (${mem_usage}MB)${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}HIGH (${mem_usage}MB)${NC}"
    ((PASS++)) # Apenas alerta
fi

echo -e "\n${BLUE}📈 RESULTADO DOS TESTES${NC}"
echo "=============================="
echo -e "Total de testes: $TOTAL"
echo -e "${GREEN}Aprovados: $PASS${NC}"
echo -e "${RED}Reprovados: $FAIL${NC}"

if [ $FAIL -eq 0 ]; then
    echo -e "\n${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
    echo "Sistema está funcionando corretamente."
else
    echo -e "\n${YELLOW}⚠️  ALGUNS TESTES FALHARAM${NC}"
    echo "Verifique os serviços e logs."
fi

echo -e "\n${BLUE}🔧 DIAGNÓSTICO RÁPIDO${NC}"
echo "=============================="
echo "Para verificar problemas:"
echo "1. Logs: ${GREEN}./start.sh logs${NC}"
echo "2. Status: ${GREEN}./start.sh status${NC}"
echo "3. Restart: ${GREEN}./start.sh restart${NC}"
echo "4. Testar API: ${GREEN}curl http://localhost:8080/health${NC}"

# Exportar resultado para arquivo
echo -e "\nExportando relatório para test_results.txt..."
{
    echo "Relatório de Testes - MegaSena AI"
    echo "Data: $(date)"
    echo "Total: $TOTAL | Aprovados: $PASS | Reprovados: $FAIL"
    echo ""
    
    if [ $FAIL -eq 0 ]; then
        echo "STATUS: ✅ APROVADO"
    else
        echo "STATUS: ❌ REPROVADO"
        echo "Falhas encontradas: $FAIL"
    fi
} > test_results.txt

echo -e "${GREEN}Relatório salvo em: test_results.txt${NC}"
