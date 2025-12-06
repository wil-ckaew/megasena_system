#!/bin/bash

# Script de instalação do MegaSena AI

set -e  # Sai em caso de erro

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║    INSTALAÇÃO MEGA-SENA AI FULLSTACK           ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se é root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}[AVISO] Executando como root${NC}"
fi

# Função para verificar e instalar dependências
install_dependency() {
    local name=$1
    local install_cmd=$2
    local check_cmd=$3
    
    echo -n "Verificando $name... "
    if eval "$check_cmd" &> /dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}NÃO ENCONTRADO${NC}"
        echo "Instalando $name..."
        eval "$install_cmd"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}$name instalado com sucesso!${NC}"
        else
            echo -e "${RED}Falha ao instalar $name${NC}"
            exit 1
        fi
    fi
}

# Atualizar sistema
echo -e "\n${BLUE}[1/6] Atualizando sistema...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get upgrade -y
elif command -v yum &> /dev/null; then
    sudo yum update -y
elif command -v dnf &> /dev/null; then
    sudo dnf update -y
fi

# Instalar Docker
echo -e "\n${BLUE}[2/6] Instalando Docker...${NC}"
install_dependency "Docker" \
    "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo usermod -aG docker \$USER" \
    "docker --version"

# Instalar Docker Compose
echo -e "\n${BLUE}[3/6] Instalando Docker Compose...${NC}"
DOCKER_COMPOSE_VERSION="v2.23.3"
install_dependency "Docker Compose" \
    "sudo curl -L \"https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose" \
    "docker-compose --version"

# Instalar dependências opcionais
echo -e "\n${BLUE}[4/6] Instalando ferramentas úteis...${NC}"

# jq para manipulação JSON
install_dependency "jq" \
    "sudo apt-get install -y jq 2>/dev/null || sudo yum install -y jq 2>/dev/null || sudo dnf install -y jq" \
    "jq --version"

# curl
install_dependency "curl" \
    "sudo apt-get install -y curl 2>/dev/null || sudo yum install -y curl 2>/dev/null || sudo dnf install -y curl" \
    "curl --version"

# Configurar ambiente
echo -e "\n${BLUE}[5/6] Configurando ambiente...${NC}"

# Verificar arquivo CSV
if [ ! -f "resultados_megasena.csv" ]; then
    echo -e "${YELLOW}Criando arquivo CSV de exemplo...${NC}"
    cat > resultados_megasena.csv << CSV_EXAMPLE
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
CSV_EXAMPLE
    echo -e "${GREEN}Arquivo CSV de exemplo criado${NC}"
else
    echo -e "${GREEN}Arquivo CSV já existe${NC}"
fi

# Dar permissões aos scripts
echo "Configurando permissões..."
chmod +x start.sh 2>/dev/null || true
chmod +x backend_rust/start.sh 2>/dev/null || true
chmod +x ia_python/start.sh 2>/dev/null || true

# Criar diretórios necessários
echo "Criando diretórios..."
mkdir -p logs
mkdir -p data
mkdir -p backup

# Build das imagens Docker
echo -e "\n${BLUE}[6/6] Construindo imagens Docker...${NC}"
echo "Isso pode levar alguns minutos..."

# Backend Rust
echo "Construindo Backend Rust..."
cd backend_rust
docker build -t megasena-backend-rust . || {
    echo -e "${RED}Falha ao construir Backend Rust${NC}"
    exit 1
}
cd ..

# IA Python
echo "Construindo IA Python..."
cd ia_python
docker build -t megasena-ia-python . || {
    echo -e "${RED}Falha ao construir IA Python${NC}"
    exit 1
}
cd ..

# Frontend Next.js
echo "Construindo Frontend..."
cd frontend_nextjs
docker build -t megasena-frontend . || {
    echo -e "${RED}Falha ao construir Frontend${NC}"
    exit 1
}
cd ..

echo -e "\n${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║    INSTALAÇÃO CONCLUÍDA COM SUCESSO!           ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "\n${BLUE}📋 PRÓXIMOS PASSOS:${NC}"
echo "1. Para iniciar o sistema:"
echo "   ${GREEN}./start.sh start${NC}"
echo ""
echo "2. Para modo desenvolvimento:"
echo "   ${GREEN}./start.sh dev${NC}"
echo ""
echo "3. Acessar o sistema:"
echo "   Frontend:  ${YELLOW}http://localhost:3000${NC}"
echo "   Backend:   ${YELLOW}http://localhost:8080${NC}"
echo "   IA Python: ${YELLOW}http://localhost:5001/docs${NC}"
echo ""
echo "4. Comandos úteis:"
echo "   ${GREEN}./start.sh status${NC}    - Ver status"
echo "   ${GREEN}./start.sh logs${NC}      - Ver logs"
echo "   ${GREEN}./start.sh stop${NC}      - Parar sistema"
echo "   ${GREEN}./start.sh restart${NC}   - Reiniciar"
echo ""
echo "${BLUE}⚠️  IMPORTANTE:${NC}"
echo "- Reinicie o terminal ou execute: ${GREEN}newgrp docker${NC}"
echo "- Configure seu arquivo CSV em: ${YELLOW}resultados_megasena.csv${NC}"
echo "- Para produção, configure SSL e firewall"
echo ""
echo "${GREEN}🎉 Sistema pronto para uso!${NC}"
