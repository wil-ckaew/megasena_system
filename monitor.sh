#!/bin/bash

# Script de monitoramento do MegaSena AI

# Configurações
LOG_FILE="monitor.log"
ALERT_FILE="alerts.log"
CHECK_INTERVAL=60  # segundos
ALERT_EMAIL=""     # configurar se quiser alertas por email

# Cores para terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Função de logging
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO") color=$BLUE ;;
        "WARN") color=$YELLOW ;;
        "ERROR") color=$RED ;;
        "SUCCESS") color=$GREEN ;;
        *) color=$NC ;;
    esac
    
    echo -e "${color}[$timestamp] [$level] $message${NC}"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Função para alerta
alert() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] ALERT: $message" >> "$ALERT_FILE"
    log "ERROR" "ALERTA: $message"
    
    # Enviar email se configurado
    if [ -n "$ALERT_EMAIL" ]; then
        echo "Alerta: $message" | mail -s "MegaSena AI Alert" "$ALERT_EMAIL"
    fi
}

# Função para verificar serviço
check_service() {
    local name="$1"
    local url="$2"
    
    if curl -s --max-time 5 "$url" > /dev/null; then
        log "SUCCESS" "$name: ONLINE"
        return 0
    else
        alert "$name: OFFLINE - $url não responde"
        return 1
    fi
}

# Função para verificar Docker
check_docker() {
    local container_name="$1"
    
    if docker ps --format '{{.Names}}' | grep -q "^$container_name$"; then
        local status=$(docker ps --format '{{.Status}}' --filter "name=$container_name")
        log "INFO" "Container $container_name: $status"
        
        # Verificar se está healthy
        if echo "$status" | grep -q "unhealthy"; then
            alert "Container $container_name: UNHEALTHY"
            return 1
        fi
        return 0
    else
        alert "Container $container_name: NÃO ENCONTRADO"
        return 1
    fi
}

# Função para verificar recursos
check_resources() {
    # CPU
    local cpu_load=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$cpu_load > 80" | bc -l) )); then
        alert "CPU alta: ${cpu_load}%"
    fi
    
    # Memória
    local mem_total=$(free -m | awk '/^Mem:/{print $2}')
    local mem_used=$(free -m | awk '/^Mem:/{print $3}')
    local mem_percent=$((mem_used * 100 / mem_total))
    
    if [ $mem_percent -gt 85 ]; then
        alert "Memória alta: ${mem_percent}% (${mem_used}MB/${mem_total}MB)"
    fi
    
    # Disco
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $disk_usage -gt 90 ]; then
        alert "Disco quase cheio: ${disk_usage}%"
    fi
    
    log "INFO" "Recursos: CPU=${cpu_load}%, Mem=${mem_percent}%, Disco=${disk_usage}%"
}

# Função para verificar logs de erro
check_error_logs() {
    local service="$1"
    local pattern="ERROR\|FAILED\|Exception\|panic"
    
    case $service in
        "backend")
            local logs=$(docker logs megasena-backend --tail 50 2>&1 | grep -i "$pattern")
            ;;
        "ia")
            local logs=$(docker logs megasena-ia --tail 50 2>&1 | grep -i "$pattern")
            ;;
        "frontend")
            local logs=$(docker logs megasena-frontend --tail 50 2>&1 | grep -i "$pattern")
            ;;
    esac
    
    if [ -n "$logs" ]; then
        alert "Erros em $service: $(echo "$logs" | tail -1)"
    fi
}

# Função para gerar relatório
generate_report() {
    local report_file="health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Relatório de Saúde - MegaSena AI"
        echo "Gerado em: $(date)"
        echo "========================================"
        echo ""
        
        echo "1. STATUS DOS SERVIÇOS:"
        echo "----------------------"
        check_service "Backend" "http://localhost:8080/health" && echo "Backend: ✅ ONLINE" || echo "Backend: ❌ OFFLINE"
        check_service "IA Python" "http://localhost:5001/health" && echo "IA Python: ✅ ONLINE" || echo "IA Python: ❌ OFFLINE"
        check_service "Frontend" "http://localhost:3000" && echo "Frontend: ✅ ONLINE" || echo "Frontend: ❌ OFFLINE"
        echo ""
        
        echo "2. CONTAINERS DOCKER:"
        echo "---------------------"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep megasena
        echo ""
        
        echo "3. RECURSOS DO SISTEMA:"
        echo "----------------------"
        echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
        echo "Memória: $(free -h | awk '/^Mem:/{print $3"/"$2}')"
        echo "Disco: $(df -h / | tail -1 | awk '{print $5}') usado"
        echo ""
        
        echo "4. ÚLTIMOS ERROS:"
        echo "----------------"
        grep "ALERT" "$ALERT_FILE" | tail -5 || echo "Nenhum alerta recente"
        echo ""
        
        echo "5. ESTATÍSTICAS DE USO:"
        echo "----------------------"
        echo "Uptime: $(uptime -p)"
        echo "API Requests (última hora): [em desenvolvimento]"
        
    } > "$report_file"
    
    log "INFO" "Relatório gerado: $report_file"
}

# Menu principal
show_menu() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════╗"
    echo "║      MONITORAMENTO MEGA-SENA AI SYSTEM         ║"
    echo "╚════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo "Opções:"
    echo "  1. Verificar status atual"
    echo "  2. Monitorar em tempo real"
    echo "  3. Gerar relatório completo"
    echo "  4. Ver logs de alerta"
    echo "  5. Ver logs de monitoramento"
    echo "  6. Configurar alertas por email"
    echo "  7. Sair"
    echo ""
}

# Modo interativo
interactive_mode() {
    while true; do
        show_menu
        read -p "Escolha uma opção: " choice
        
        case $choice in
            1)
                echo ""
                log "INFO" "Verificando status atual..."
                check_service "Backend" "http://localhost:8080/health"
                check_service "IA Python" "http://localhost:5001/health"
                check_service "Frontend" "http://localhost:3000"
                check_docker "megasena-backend"
                check_docker "megasena-ia"
                check_docker "megasena-frontend"
                check_resources
                echo ""
                ;;
            2)
                echo ""
                log "INFO" "Iniciando monitoramento em tempo real (Ctrl+C para parar)"
                echo "Intervalo de verificação: ${CHECK_INTERVAL}s"
                echo ""
                
                trap 'log "INFO" "Monitoramento interrompido"; exit 0' INT
                
                while true; do
                    echo "=== $(date) ==="
                    check_service "Backend" "http://localhost:8080/health"
                    check_service "IA Python" "http://localhost:5001/health"
                    check_resources
                    echo ""
                    sleep $CHECK_INTERVAL
                done
                ;;
            3)
                echo ""
                generate_report
                echo "Relatório salvo no arquivo atual"
                ;;
            4)
                echo ""
                if [ -f "$ALERT_FILE" ]; then
                    echo "Últimos alertas:"
                    echo "================"
                    tail -20 "$ALERT_FILE"
                else
                    echo "Nenhum alerta registrado"
                fi
                ;;
            5)
                echo ""
                if [ -f "$LOG_FILE" ]; then
                    echo "Últimos logs:"
                    echo "============="
                    tail -20 "$LOG_FILE"
                else
                    echo "Nenhum log registrado"
                fi
                ;;
            6)
                echo ""
                read -p "Digite o email para alertas: " ALERT_EMAIL
                log "INFO" "Email de alerta configurado: $ALERT_EMAIL"
                ;;
            7)
                echo ""
                log "INFO" "Saindo..."
                exit 0
                ;;
            *)
                echo "Opção inválida"
                ;;
        esac
        
        echo ""
        read -p "Pressione Enter para continuar..."
    done
}

# Modo automático (para cron)
auto_mode() {
    log "INFO" "Iniciando verificação automática"
    
    # Verificar serviços
    check_service "Backend" "http://localhost:8080/health"
    check_service "IA Python" "http://localhost:5001/health"
    check_service "Frontend" "http://localhost:3000"
    
    # Verificar containers
    check_docker "megasena-backend"
    check_docker "megasena-ia"
    check_docker "megasena-frontend"
    
    # Verificar recursos
    check_resources
    
    # Verificar logs de erro
    check_error_logs "backend"
    check_error_logs "ia"
    check_error_logs "frontend"
    
    log "INFO" "Verificação automática concluída"
}

# Verificar argumentos
if [ "$1" = "--auto" ]; then
    auto_mode
else
    interactive_mode
fi
