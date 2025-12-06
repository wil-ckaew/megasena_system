#!/bin/bash

# ============================================
# MEGA-SENA AI - SCRIPT DE CONTROLE COMPLETO
# ============================================

# Configurações
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções de logging
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "   🎰 MEGA-SENA AI - SISTEMA FULLSTACK"
    echo "=================================================="
    echo "   🦀 Backend Rust  | 🤖 IA Python | ⚛️ Next.js"
    echo "=================================================="
    echo -e "${NC}"
}

# Verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker não encontrado!"
        echo "Instale Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    log_success "Docker: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
    
    # Docker Compose
    if ! command -v docker compose &> /dev/null; then
        # Tentar docker compose v2
        if ! docker compose version &> /dev/null; then
            log_error "Docker Compose não encontrado!"
            echo "Instale Docker Compose: https://docs.docker.com/compose/install/"
            exit 1
        else
            DOCKER_COMPOSE_CMD="docker compose"
            log_success "Docker Compose v2 disponível"
        fi
    else
        DOCKER_COMPOSE_CMD="docker compose"
        log_success "Docker Compose: $(docker compose --version | cut -d' ' -f3 | cut -d',' -f1)"
    fi
    
    # Verificar arquivo CSV
    if [ -f "$PROJECT_DIR/resultados_megasena.csv" ]; then
        log_success "Arquivo CSV encontrado: resultados_megasena.csv"
    else
        log_warn "Arquivo CSV não encontrado na raiz"
        echo "Crie um arquivo resultados_megasena.csv com os dados históricos"
    fi
    
    # Verificar memória disponível
    MEM_AVAILABLE=$(free -m | awk '/^Mem:/{print $7}')
    if [ "$MEM_AVAILABLE" -lt 2048 ]; then
        log_warn "Memória disponível baixa: ${MEM_AVAILABLE}MB"
        echo "Recomendado: Mínimo 2GB de RAM livre"
    fi
}

# Iniciar serviços
start_services() {
    print_banner
    check_dependencies
    
    log_info "Iniciando serviços Docker Compose..."
    
    cd "$PROJECT_DIR"
    
    # Verificar se os serviços já estão rodando
    if [ "$($DOCKER_COMPOSE_CMD ps -q)" ]; then
        log_warn "Serviços já estão em execução"
        echo "Use: ./start.sh restart para reiniciar"
        exit 1
    fi
    
    # Iniciar serviços
    $DOCKER_COMPOSE_CMD up -d
    
    if [ $? -eq 0 ]; then
        log_success "Serviços iniciados com sucesso!"
        show_status
        show_endpoints
        show_quick_test
    else
        log_error "Falha ao iniciar serviços"
        exit 1
    fi
}

# Parar serviços
stop_services() {
    log_info "Parando serviços..."
    
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE_CMD down
    
    if [ $? -eq 0 ]; then
        log_success "Serviços parados com sucesso"
    else
        log_error "Falha ao parar serviços"
    fi
}

# Reiniciar serviços
restart_services() {
    log_info "Reiniciando serviços..."
    
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE_CMD restart
    
    if [ $? -eq 0 ]; then
        log_success "Serviços reiniciados"
        sleep 3
        show_status
    else
        log_error "Falha ao reiniciar serviços"
    fi
}

# Status dos serviços
show_status() {
    log_info "Status dos serviços:"
    echo ""
    
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE_CMD ps
    
    echo ""
    log_info "Logs recentes:"
    $DOCKER_COMPOSE_CMD logs --tail=5
}

# Mostrar endpoints
show_endpoints() {
    echo ""
    echo -e "${BLUE}🌐 ENDPOINTS DISPONÍVEIS:${NC}"
    echo "========================================"
    echo -e "${GREEN}Frontend:${NC}      http://localhost:3000"
    echo -e "${CYAN}Backend Rust:${NC}   http://localhost:8080"
    echo -e "${YELLOW}IA Python:${NC}     http://localhost:5001"
    echo -e "${YELLOW}Python Docs:${NC}   http://localhost:5001/docs"
    echo "========================================"
    echo ""
}

# Teste rápido da API
show_quick_test() {
    echo -e "${BLUE}🧪 TESTE RÁPIDO DA API:${NC}"
    echo "========================================"
    echo "Para testar a API, execute:"
    echo ""
    echo "curl -X POST http://localhost:8080/api/generate \\"
    echo '  -H "Content-Type: application/json" \'
    echo '  -d '\''{"day": 15}'\'' | jq'
    echo ""
    echo "Ou use o frontend em: http://localhost:3000"
    echo "========================================"
}

# Limpar tudo
clean_all() {
    log_info "Limpando ambiente Docker..."
    
    cd "$PROJECT_DIR"
    
    # Parar e remover containers
    $DOCKER_COMPOSE_CMD down -v
    
    # Remover imagens
    docker rmi -f megasena-backend-rust megasena-ia-python megasena-frontend 2>/dev/null || true
    
    # Limpar volumes não usados
    docker volume prune -f
    
    # Limpar network
    docker network prune -f
    
    log_success "Ambiente Docker limpo"
}

# Modo desenvolvimento
dev_mode() {
    print_banner
    log_info "Iniciando modo desenvolvimento..."
    
    # Verificar dependências de desenvolvimento
    log_info "Verificando ferramentas de desenvolvimento..."
    
    # Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js não encontrado!"
        echo "Instale Node.js: https://nodejs.org/"
        exit 1
    fi
    log_success "Node.js: $(node --version)"
    
    # npm
    if ! command -v npm &> /dev/null; then
        log_error "npm não encontrado!"
        exit 1
    fi
    log_success "npm: $(npm --version)"
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 não encontrado!"
        echo "Instale Python 3: https://www.python.org/"
        exit 1
    fi
    log_success "Python: $(python3 --version)"
    
    # Rust (opcional para backend)
    if ! command -v cargo &> /dev/null; then
        log_warn "Rust não encontrado (backend usará Docker)"
    else
        log_success "Rust: $(rustc --version | cut -d' ' -f2)"
    fi
    
    # Iniciar serviços em segundo plano
    log_info "Iniciando serviços em modo desenvolvimento..."
    
    # 1. Iniciar Backend Rust (se disponível)
    if command -v cargo &> /dev/null; then
        log_info "Iniciando Backend Rust..."
        cd "$PROJECT_DIR/backend_rust"
        cargo run &
        RUST_PID=$!
        log_success "Backend Rust iniciado (PID: $RUST_PID)"
    else
        log_warn "Rust não disponível - Backend não iniciado"
        RUST_PID=""
    fi
    
    # 2. Iniciar IA Python
    log_info "Iniciando IA Python..."
    cd "$PROJECT_DIR/ia_python"
    
    # Criar/ativar venv
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # Instalar dependências
    if [ ! -f "requirements_installed" ]; then
        pip install -r requirements.txt
        touch requirements_installed
    fi
    
    # Iniciar servidor
    python3 main.py &
    PYTHON_PID=$!
    log_success "IA Python iniciada (PID: $PYTHON_PID)"
    
    # 3. Iniciar Frontend
    log_info "Iniciando Frontend Next.js..."
    cd "$PROJECT_DIR/frontend_nextjs"
    
    # Instalar dependências
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Iniciar servidor
    npm run dev &
    FRONTEND_PID=$!
    log_success "Frontend iniciado (PID: $FRONTEND_PID)"
    
    # Mostrar informações
    echo ""
    echo -e "${GREEN}✅ TODOS OS SERVIÇOS INICIADOS!${NC}"
    echo ""
    show_endpoints
    
    echo -e "${YELLOW}📝 LOGS DOS SERVIÇOS:${NC}"
    echo "Para ver logs do Backend Rust: tail -f backend_rust/target/debug/*.log"
    echo "Para ver logs da IA Python:    tail -f ia_python/*.log"
    echo "Para ver logs do Frontend:     tail -f frontend_nextjs/.next/*.log"
    echo ""
    echo -e "${RED}🛑 PARA PARAR:${NC} Pressione Ctrl+C e execute: kill $RUST_PID $PYTHON_PID $FRONTEND_PID 2>/dev/null"
    echo ""
    
    # Aguardar Ctrl+C
    wait
}

# Build das imagens
build_images() {
    log_info "Construindo imagens Docker..."
    
    cd "$PROJECT_DIR"
    
    # Backend Rust
    log_info "Construindo Backend Rust..."
    cd backend_rust
    docker build -t megasena-backend-rust .
    
    # IA Python
    log_info "Construindo IA Python..."
    cd ../ia_python
    docker build -t megasena-ia-python .
    
    # Frontend
    log_info "Construindo Frontend..."
    cd ../frontend_nextjs
    docker build -t megasena-frontend .
    
    cd "$PROJECT_DIR"
    log_success "Todas as imagens construídas com sucesso!"
}

# Atualizar código
update_code() {
    log_info "Atualizando código dos serviços..."
    
    # Parar serviços
    stop_services
    
    # Rebuild imagens
    build_images
    
    # Iniciar serviços
    start_services
}

# Monitorar logs
monitor_logs() {
    log_info "Monitorando logs (Ctrl+C para sair)..."
    echo ""
    
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE_CMD logs -f
}

# Menu de ajuda
show_help() {
    print_banner
    echo "Uso: ./start.sh [COMANDO]"
    echo ""
    echo "Comandos disponíveis:"
    echo ""
    echo -e "${GREEN}  start${NC}     - Iniciar todos os serviços (Docker)"
    echo -e "${GREEN}  stop${NC}      - Parar todos os serviços"
    echo -e "${GREEN}  restart${NC}   - Reiniciar serviços"
    echo -e "${GREEN}  status${NC}    - Mostrar status dos serviços"
    echo -e "${GREEN}  logs${NC}      - Monitorar logs em tempo real"
    echo -e "${GREEN}  build${NC}     - Construir imagens Docker"
    echo -e "${GREEN}  clean${NC}     - Limpar ambiente Docker completamente"
    echo -e "${GREEN}  update${NC}    - Atualizar código e reiniciar"
    echo -e "${GREEN}  dev${NC}       - Modo desenvolvimento (local sem Docker)"
    echo -e "${GREEN}  test${NC}      - Testar APIs"
    echo -e "${GREEN}  help${NC}      - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  ./start.sh start    # Iniciar sistema completo"
    echo "  ./start.sh dev      # Modo desenvolvimento"
    echo "  ./start.sh logs     # Ver logs"
    echo ""
}

# Testar APIs
test_apis() {
    log_info "Testando APIs..."
    echo ""
    
    # Testar Backend Rust
    echo -e "${CYAN}1. Testando Backend Rust:${NC}"
    if curl -s http://localhost:8080/health > /dev/null; then
        echo -e "  ${GREEN}✅ OK${NC} - Backend respondendo"
        curl -s http://localhost:8080/health | jq . 2>/dev/null || curl -s http://localhost:8080/health
    else
        echo -e "  ${RED}❌ OFFLINE${NC} - Backend não respondendo"
    fi
    echo ""
    
    # Testar IA Python
    echo -e "${YELLOW}2. Testando IA Python:${NC}"
    if curl -s http://localhost:5001/health > /dev/null; then
        echo -e "  ${GREEN}✅ OK${NC} - IA Python respondendo"
        curl -s http://localhost:5001/health | jq . 2>/dev/null || curl -s http://localhost:5001/health
    else
        echo -e "  ${RED}❌ OFFLINE${NC} - IA Python não respondendo"
    fi
    echo ""
    
    # Testar geração de jogo
    echo -e "${GREEN}3. Testando geração de jogo:${NC}"
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "  Gerando jogo para dia 15..."
        curl -X POST http://localhost:8080/api/generate \
            -H "Content-Type: application/json" \
            -d '{"day": 15}' \
            -s | jq '.games[0].numbers' 2>/dev/null || \
        curl -X POST http://localhost:8080/api/generate \
            -H "Content-Type: application/json" \
            -d '{"day": 15}' \
            -s | grep -o '\[.*\]'
        
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✅ OK${NC} - Jogo gerado com sucesso"
        else
            echo -e "  ${RED}❌ FALHA${NC} - Erro ao gerar jogo"
        fi
    fi
    echo ""
    
    log_success "Testes concluídos!"
}

# Processar comando
case "$1" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        monitor_logs
        ;;
    "build")
        build_images
        ;;
    "clean")
        clean_all
        ;;
    "update")
        update_code
        ;;
    "dev")
        dev_mode
        ;;
    "test")
        test_apis
        ;;
    "help"|"")
        show_help
        ;;
    *)
        log_error "Comando desconhecido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
