#!/bin/bash

# Script de restauração do MegaSena AI

BACKUP_DIR="./backups"
RESTORE_DIR="./restore_temp"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar argumento
if [ -z "$1" ]; then
    echo -e "${RED}Erro: Especifique o arquivo de backup${NC}"
    echo ""
    echo "Uso: ./restore.sh <arquivo_backup.tar.gz>"
    echo ""
    echo "Backups disponíveis:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "   (nenhum backup encontrado)"
    exit 1
fi

BACKUP_FILE="$1"
if [[ ! "$BACKUP_FILE" == *.tar.gz ]]; then
    # Se não tem extensão, procurar no diretório de backups
    if [ -f "$BACKUP_DIR/${BACKUP_FILE}.tar.gz" ]; then
        BACKUP_FILE="$BACKUP_DIR/${BACKUP_FILE}.tar.gz"
    elif [ -f "$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_FILE"
    else
        echo -e "${RED}Erro: Arquivo não encontrado: $BACKUP_FILE${NC}"
        exit 1
    fi
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Erro: Arquivo de backup não encontrado: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}"
echo "╔════════════════════════════════════════════════╗"
echo "║      RESTAURAÇÃO MEGA-SENA AI SYSTEM           ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo "Backup selecionado: $BACKUP_FILE"
echo ""

# Confirmar restauração
read -p "⚠️  Esta ação irá sobrescrever dados atuais. Continuar? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Restauração cancelada."
    exit 0
fi

# Parar serviços se estiverem rodando
echo "1. Parando serviços..."
docker-compose down 2>/dev/null || true

# Criar diretório temporário
echo "2. Extraindo backup..."
rm -rf "$RESTORE_DIR"
mkdir -p "$RESTORE_DIR"
tar xzf "$BACKUP_FILE" -C "$RESTORE_DIR" 2>/dev/null || {
    echo -e "${RED}Erro ao extrair backup${NC}"
    exit 1
}

# Encontrar diretório de backup extraído
BACKUP_CONTENT=$(find "$RESTORE_DIR" -name "metadata.txt" -type f | head -1 | xargs dirname 2>/dev/null)
if [ -z "$BACKUP_CONTENT" ]; then
    BACKUP_CONTENT=$(ls -d "$RESTORE_DIR"/*/ 2>/dev/null | head -1)
fi

if [ -z "$BACKUP_CONTENT" ]; then
    echo -e "${RED}Erro: Não foi possível encontrar conteúdo do backup${NC}"
    exit 1
fi

echo "Conteúdo extraído em: $BACKUP_CONTENT"
echo ""

# 3. Restaurar arquivo CSV
echo "3. Restaurando arquivo CSV..."
if [ -f "$BACKUP_CONTENT/resultados_megasena.csv" ]; then
    cp -v "$BACKUP_CONTENT/resultados_megasena.csv" ./
    echo -e "   ${GREEN}✅ CSV restaurado${NC}"
else
    echo -e "   ${YELLOW}⚠️  CSV não encontrado no backup${NC}"
fi

# 4. Restaurar configurações
echo "4. Restaurando configurações..."
if [ -d "$BACKUP_CONTENT/config" ]; then
    cp -v "$BACKUP_CONTENT/config/"* ./ 2>/dev/null || true
    echo -e "   ${GREEN}✅ Configurações restauradas${NC}"
fi

# 5. Restaurar código fonte (opcional)
read -p "Restaurar código fonte? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "5. Restaurando código fonte..."
    
    # Backend Rust
    if [ -d "$BACKUP_CONTENT/src/backend_rust" ]; then
        echo "   - Backend Rust..."
        rm -rf backend_rust/src
        rm -f backend_rust/Cargo.toml
        rm -f backend_rust/Dockerfile
        cp -r "$BACKUP_CONTENT/src/backend_rust/"* backend_rust/ 2>/dev/null || true
    fi
    
    # IA Python
    if [ -d "$BACKUP_CONTENT/src/ia_python" ]; then
        echo "   - IA Python..."
        rm -rf ia_python/*.py
        rm -f ia_python/requirements.txt
        rm -f ia_python/Dockerfile
        cp "$BACKUP_CONTENT/src/ia_python/"* ia_python/ 2>/dev/null || true
    fi
    
    # Frontend
    if [ -d "$BACKUP_CONTENT/src/frontend_nextjs" ]; then
        echo "   - Frontend..."
        rm -rf frontend_nextjs/pages
        rm -rf frontend_nextjs/components
        rm -rf frontend_nextjs/styles
        rm -f frontend_nextjs/package*.json
        rm -f frontend_nextjs/*.config.js
        rm -f frontend_nextjs/Dockerfile
        cp -r "$BACKUP_CONTENT/src/frontend_nextjs/"* frontend_nextjs/ 2>/dev/null || true
    fi
    
    echo -e "   ${GREEN}✅ Código fonte restaurado${NC}"
fi

# 6. Restaurar volumes Docker (opcional)
read -p "Restaurar dados Docker (volumes)? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "6. Restaurando volumes Docker..."
    
    if [ -d "$BACKUP_CONTENT/docker_volumes" ]; then
        for volume_file in "$BACKUP_CONTENT/docker_volumes"/*.tar.gz; do
            if [ -f "$volume_file" ]; then
                volume_name=$(basename "$volume_file" .tar.gz)
                echo "   - Volume: $volume_name"
                
                # Criar volume se não existir
                docker volume create "$volume_name" 2>/dev/null || true
                
                # Restaurar dados
                docker run --rm -v "$volume_name:/data" -v "$volume_file:/backup.tar.gz" \
                    alpine sh -c "tar xzf /backup.tar.gz -C /data 2>/dev/null || true"
                    
                echo "     ${GREEN}✅ Restaurado${NC}"
            fi
        done
    fi
fi

# 7. Limpar diretório temporário
echo "7. Limpando arquivos temporários..."
rm -rf "$RESTORE_DIR"

# 8. Rebuild das imagens
echo "8. Reconstruindo imagens Docker..."
echo "   Esta etapa pode levar alguns minutos..."
./start.sh build 2>/dev/null || {
    echo -e "   ${YELLOW}⚠️  Falha no build automático${NC}"
    echo "   Execute manualmente: ./start.sh build"
}

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║     RESTAURAÇÃO CONCLUÍDA COM SUCESSO!         ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "✅ Restauração completa!"
echo ""
echo "📋 Próximos passos:"
echo "1. Iniciar o sistema:"
echo "   ${GREEN}./start.sh start${NC}"
echo ""
echo "2. Verificar status:"
echo "   ${GREEN}./start.sh status${NC}"
echo ""
echo "3. Testar sistema:"
echo "   ${GREEN}./start.sh test${NC}"
echo ""
echo "4. Acessar:"
echo "   Frontend:  ${YELLOW}http://localhost:3000${NC}"
echo ""
echo "⚠️  Nota: Se encontrar problemas, verifique os logs:"
echo "   ${GREEN}./start.sh logs${NC}"
