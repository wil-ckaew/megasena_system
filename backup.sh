#!/bin/bash

# Script de backup do MegaSena AI

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="megasena_backup_$TIMESTAMP"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}"
echo "╔════════════════════════════════════════════════╗"
echo "║        BACKUP MEGA-SENA AI SYSTEM              ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Criar diretório de backup
mkdir -p "$BACKUP_PATH"

echo "Iniciando backup em: $BACKUP_PATH"
echo ""

# 1. Backup do arquivo CSV
echo "1. Backup do arquivo CSV..."
cp -v resultados_megasena.csv "$BACKUP_PATH/" 2>/dev/null && \
    echo -e "   ${GREEN}✅ CSV backup concluído${NC}" || \
    echo -e "   ${RED}❌ Falha no backup do CSV${NC}"

# 2. Backup das configurações
echo "2. Backup das configurações..."
mkdir -p "$BACKUP_PATH/config"
cp -v docker-compose.yml "$BACKUP_PATH/config/" 2>/dev/null
cp -v start.sh "$BACKUP_PATH/config/" 2>/dev/null
cp -v install.sh "$BACKUP_PATH/config/" 2>/dev/null
echo -e "   ${GREEN}✅ Configurações backup concluído${NC}"

# 3. Backup do código fonte
echo "3. Backup do código fonte..."
mkdir -p "$BACKUP_PATH/src"

# Backend Rust
echo "   - Backend Rust..."
mkdir -p "$BACKUP_PATH/src/backend_rust"
cp -rv backend_rust/src "$BACKUP_PATH/src/backend_rust/" 2>/dev/null
cp -v backend_rust/Cargo.toml "$BACKUP_PATH/src/backend_rust/" 2>/dev/null
cp -v backend_rust/Dockerfile "$BACKUP_PATH/src/backend_rust/" 2>/dev/null

# IA Python
echo "   - IA Python..."
mkdir -p "$BACKUP_PATH/src/ia_python"
cp -v ia_python/*.py "$BACKUP_PATH/src/ia_python/" 2>/dev/null
cp -v ia_python/requirements.txt "$BACKUP_PATH/src/ia_python/" 2>/dev/null
cp -v ia_python/Dockerfile "$BACKUP_PATH/src/ia_python/" 2>/dev/null

# Frontend
echo "   - Frontend Next.js..."
mkdir -p "$BACKUP_PATH/src/frontend_nextjs"
cp -rv frontend_nextjs/pages "$BACKUP_PATH/src/frontend_nextjs/" 2>/dev/null
cp -rv frontend_nextjs/components "$BACKUP_PATH/src/frontend_nextjs/" 2>/dev/null
cp -rv frontend_nextjs/styles "$BACKUP_PATH/src/frontend_nextjs/" 2>/dev/null
cp -v frontend_nextjs/package*.json "$BACKUP_PATH/src/frontend_nextjs/" 2>/dev/null
cp -v frontend_nextjs/*.config.js "$BACKUP_PATH/src/frontend_nextjs/" 2>/dev/null
cp -v frontend_nextjs/Dockerfile "$BACKUP_PATH/src/frontend_nextjs/" 2>/dev/null

echo -e "   ${GREEN}✅ Código fonte backup concluído${NC}"

# 4. Backup dos logs (se existirem)
echo "4. Backup dos logs..."
mkdir -p "$BACKUP_PATH/logs"
cp -v logs/*.log "$BACKUP_PATH/logs/" 2>/dev/null || true
docker-compose logs --no-color > "$BACKUP_PATH/logs/docker_logs.txt" 2>/dev/null || true
echo -e "   ${GREEN}✅ Logs backup concluído${NC}"

# 5. Backup dos dados do Docker
echo "5. Backup dos volumes Docker..."
mkdir -p "$BACKUP_PATH/docker_volumes"

# Listar volumes
docker volume ls --format "{{.Name}}" | grep megasena | while read volume; do
    echo "   - Volume: $volume"
    docker run --rm -v "$volume:/data" -v "$BACKUP_PATH/docker_volumes:/backup" \
        alpine tar czf "/backup/${volume}.tar.gz" -C /data . 2>/dev/null && \
        echo "     ${GREEN}✅ OK${NC}" || \
        echo "     ${YELLOW}⚠️  Vazio ou sem permissão${NC}"
done

# 6. Criar arquivo de metadados
echo "6. Criando metadados..."
cat > "$BACKUP_PATH/metadata.txt" << META
Backup: $BACKUP_NAME
Data: $(date)
Sistema: MegaSena AI FullStack
Versão: 1.0.0
Usuário: $(whoami)
Hostname: $(hostname)

Conteúdo:
- resultados_megasena.csv
- Configurações do sistema
- Código fonte completo
- Logs do sistema
- Volumes Docker

Comando para restaurar:
./restore.sh $BACKUP_NAME

META

# 7. Compactar backup
echo "7. Compactando backup..."
cd "$BACKUP_DIR"
tar czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME" 2>/dev/null

# Remover diretório temporário
cd ..
rm -rf "$BACKUP_PATH"

# Calcular tamanho
BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║        BACKUP CONCLUÍDO COM SUCESSO!           ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "📁 Backup salvo em: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "📊 Tamanho: $BACKUP_SIZE"
echo ""
echo "📋 Conteúdo do backup:"
echo "   • Arquivo CSV principal"
echo "   • Configurações do sistema"
echo "   • Código fonte completo"
echo "   • Logs do sistema"
echo "   • Volumes Docker"
echo ""
echo "🔄 Para restaurar: ./restore.sh ${BACKUP_NAME}.tar.gz"
echo ""
echo "💾 Backups disponíveis:"
ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "   (nenhum backup encontrado)"
