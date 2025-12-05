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

# Função para parar e remover todos os containers
remove_containers() {
    echo -e "\n${YELLOW}1. Parando todos os containers...${NC}"
    docker stop $(docker ps -aq) 2>/dev/null
    
    echo -e "${YELLOW}2. Removendo todos os containers...${NC}"
    docker rm $(docker ps -aq) 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Todos os containers foram removidos${NC}"
    else
        echo -e "${RED}✗ Nenhum container para remover${NC}"
    fi
}

# Função para remover todas as imagens
remove_images() {
    echo -e "\n${YELLOW}3. Removendo todas as imagens Docker...${NC}"
    
    # Verificar se existem imagens
    if [ "$(docker images -q)" ]; then
        docker rmi -f $(docker images -aq) 2>/dev/null
        echo -e "${GREEN}✓ Todas as imagens foram removidas${NC}"
    else
        echo -e "${RED}✗ Nenhuma imagem para remover${NC}"
    fi
}

# Função para limpar volumes, redes e cache
clean_system() {
    echo -e "\n${YELLOW}4. Limpando volumes não utilizados...${NC}"
    docker volume prune -f
    
    echo -e "${YELLOW}5. Limpando redes não utilizadas...${NC}"
    docker network prune -f
    
    echo -e "${YELLOW}6. Limpando cache de build...${NC}"
    docker builder prune -f
    
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

# Função principal
main() {
    check_docker
    
    echo -e "${RED}Atenção: Esta ação irá remover TODOS os containers e imagens Docker!${NC}"
    read -p "Tem certeza que deseja continuar? (s/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        remove_containers
        remove_images
        clean_system
        show_status
    else
        echo -e "${YELLOW}Operação cancelada pelo usuário${NC}"
        exit 0
    fi
}

# Executar função principal
main
