#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Docker Cleanup Script ===${NC}"

# Função para verificar se o Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Erro: Docker não está instalado!${NC}"
        exit 1
    fi
}

# Função para parar todos os containers
stop_all_containers() {
    echo -e "\n${YELLOW}1. Parando todos os containers...${NC}"
    # Usar xargs para evitar erros quando não há containers
    docker ps -q 2>/dev/null | xargs -r docker stop
    echo -e "${GREEN}✓ Todos os containers foram parados${NC}"
}

# Função para remover todos os containers
remove_all_containers() {
    echo -e "\n${YELLOW}2. Removendo todos os containers...${NC}"
    docker container ls -aq 2>/dev/null | xargs -r docker rm -f
    echo -e "${GREEN}✓ Todos os containers foram removidos${NC}"
}

# Função para remover todas as imagens
remove_all_images() {
    echo -e "\n${YELLOW}3. Removendo todas as imagens Docker...${NC}"
    docker images -q 2>/dev/null | xargs -r docker rmi -f
    echo -e "${GREEN}✓ Todas as imagens foram removidas${NC}"
}

# Função para limpar volumes, redes e cache
clean_system() {
    echo -e "\n${YELLOW}4. Limpando volumes não utilizados...${NC}"
    docker volume prune -f
    
    echo -e "\n${YELLOW}5. Limpando redes não utilizadas...${NC}"
    docker network prune -f
    
    echo -e "\n${YELLOW}6. Limpando cache de build...${NC}"
    docker builder prune -af
    
    echo -e "\n${YELLOW}7. Limpando tudo (sistema completo)...${NC}"
    docker system prune -af --volumes
    
    echo -e "\n${GREEN}✓ Sistema Docker limpo com sucesso!${NC}"
}

# Função para exibir status após limpeza
show_status() {
    echo -e "\n${YELLOW}=== Status após limpeza ===${NC}"
    
    echo -e "\n${YELLOW}Containers:${NC}"
    docker ps -a
    
    echo -e "\n${YELLOW}Imagens:${NC}"
    docker images
    
    echo -e "\n${YELLOW}Volumes:${NC}"
    docker volume ls
    
    echo -e "\n${YELLOW}Redes:${NC}"
    docker network ls
}

# Função para remover containers por nome específico (se necessário)
remove_specific_containers() {
    echo -e "\n${YELLOW}Removendo containers específicos...${NC}"
    # Lista de containers que ainda estão rodando
    docker ps --format "{{.Names}}" | while read container; do
        echo -e "Removendo: ${container}"
        docker stop "$container" && docker rm "$container"
    done
}

# Função principal
main() {
    check_docker
    
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║ ATENÇÃO: Esta ação irá remover TODOS os containers,      ║${NC}"
    echo -e "${RED}║ imagens, volumes e redes Docker!                         ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    
    read -p "Tem certeza que deseja continuar? (s/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        stop_all_containers
        remove_all_containers
        remove_all_images
        clean_system
        
        # Verificar se ainda há containers
        if [ "$(docker ps -aq)" ]; then
            remove_specific_containers
        fi
        
        show_status
    else
        echo -e "${YELLOW}Operação cancelada pelo usuário${NC}"
        exit 0
    fi
}

# Executar função principal
main
