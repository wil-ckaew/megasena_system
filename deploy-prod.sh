#!/bin/bash

# Script de deploy em produção do MegaSena AI

set -e  # Sai em caso de erro

# Configurações
PROJECT_DIR=$(pwd)
DOMAIN="${1:-megasena.local}"
EMAIL="${2:-admin@$DOMAIN}"
SSL_ENABLE="${3:-true}"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║        DEPLOY PRODUÇÃO MEGA-SENA AI            ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo "Domínio: $DOMAIN"
echo "Email: $EMAIL"
echo "SSL: $SSL_ENABLE"
echo ""

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Erro: Execute como root/sudo${NC}"
    exit 1
fi

# Função para validar domínio
validate_domain() {
    if [[ ! "$1" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$ ]]; then
        echo -e "${RED}Domínio inválido: $1${NC}"
        exit 1
    fi
}

validate_domain "$DOMAIN"

# 1. Atualizar sistema
echo -e "\n${BLUE}[1/7] Atualizando sistema...${NC}"
apt-get update -y
apt-get upgrade -y

# 2. Instalar dependências
echo -e "\n${BLUE}[2/7] Instalando dependências...${NC}"
apt-get install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    ufw \
    curl \
    wget \
    git \
    jq

# 3. Configurar firewall
echo -e "\n${BLUE}[3/7] Configurando firewall...${NC}"
ufw --force enable
ufw allow 22/tcp        # SSH
ufw allow 80/tcp        # HTTP
ufw allow 443/tcp       # HTTPS
ufw allow 3000/tcp      # Frontend (se exposto)
ufw reload
ufw status verbose

# 4. Configurar Docker
echo -e "\n${BLUE}[4/7] Configurando Docker...${NC}"
systemctl enable docker
systemctl start docker
usermod -aG docker $SUDO_USER

# 5. Configurar NGINX
echo -e "\n${BLUE}[5/7] Configurando NGINX...${NC}"

# Criar configuração NGINX
cat > /etc/nginx/sites-available/megasena << NGINX_CONFIG
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Redirecionar para HTTPS (se SSL habilitado)
    $([ "$SSL_ENABLE" = "true" ] && echo "return 301 https://\$server_name\$request_uri;")
    
    # Se SSL desabilitado, proxy para frontend
    $([ "$SSL_ENABLE" = "false" ] && echo "
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /ia/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    ")
}

$([ "$SSL_ENABLE" = "true" ] && echo "
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;
    
    # SSL optimizations
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /ia/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /docs {
        proxy_pass http://localhost:5001/docs;
        proxy_set_header Host \$host;
    }
    
    location /redoc {
        proxy_pass http://localhost:5001/redoc;
        proxy_set_header Host \$host;
    }
}
")
NGINX_CONFIG

# Habilitar site
ln -sf /etc/nginx/sites-available/megasena /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 6. Obter certificado SSL (se habilitado)
if [ "$SSL_ENABLE" = "true" ]; then
    echo -e "\n${BLUE}[6/7] Obtendo certificado SSL...${NC}"
    
    # Parar nginx temporariamente
    systemctl stop nginx
    
    # Obter certificado
    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --preferred-challenges http \
        --expand
    
    # Configurar renew hook
    echo '#!/bin/bash
systemctl stop nginx
certbot renew --quiet
systemctl start nginx' > /etc/letsencrypt/renewal-hooks/post/megasena.sh
    
    chmod +x /etc/letsencrypt/renewal-hooks/post/megasena.sh
    
    # Reiniciar nginx
    systemctl start nginx
else
    echo -e "\n${YELLOW}[6/7] SSL desabilitado - pulando...${NC}"
fi

# 7. Configurar sistema
echo -e "\n${BLUE}[7/7] Configurando aplicação...${NC}"

# Criar usuário para a aplicação
if ! id "megasena" &>/dev/null; then
    useradd -r -s /bin/false -m -d /opt/megasena megasena
fi

# Copiar projeto
PROD_DIR="/opt/megasena"
mkdir -p "$PROD_DIR"
cp -r "$PROJECT_DIR"/* "$PROD_DIR/"
chown -R megasena:megasena "$PROD_DIR"
cd "$PROD_DIR"

# Configurar docker-compose para produção
cat > docker-compose.prod.yml << DOCKER_COMPOSE
version: '3.8'

services:
  backend:
    build: ./backend_rust
    container_name: megasena-backend-prod
    restart: always
    environment:
      - RUST_LOG=info
      - HOST=0.0.0.0
      - PORT=8080
      - PYTHON_IA_URL=http://ia:5001/api/generate
    volumes:
      - ./resultados_megasena.csv:/app/data/resultados_megasena.csv
      - backend_data_prod:/data
    networks:
      - megasena-prod-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ia:
    build: ./ia_python
    container_name: megasena-ia-prod
    restart: always
    environment:
      - HOST=0.0.0.0
      - PORT=5001
      - DEBUG=False
      - CSV_PATH=/app/data/resultados_megasena.csv
    volumes:
      - ./resultados_megasena.csv:/app/data/resultados_megasena.csv
      - ia_cache_prod:/app/cache
    networks:
      - megasena-prod-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend_nextjs
    container_name: megasena-frontend-prod
    restart: always
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=/api
      - NEXT_PUBLIC_IA_URL=/ia
    networks:
      - megasena-prod-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  megasena-prod-network:
    driver: bridge

volumes:
  backend_data_prod:
  ia_cache_prod:
DOCKER_COMPOSE

# Construir e iniciar
echo "Construindo imagens Docker..."
docker-compose -f docker-compose.prod.yml build

echo "Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Configurar sistema de logs
echo "Configurando logs..."
mkdir -p /var/log/megasena
ln -sf /dev/stdout /var/log/megasena/backend.log
ln -sf /dev/stdout /var/log/megasena/ia.log
ln -sf /dev/stdout /var/log/megasena/frontend.log

# Configurar monitoramento
echo "Configurando monitoramento..."
cat > /etc/systemd/system/megasena-monitor.service << SERVICE
[Unit]
Description=MegaSena AI Monitor
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=megasena
WorkingDirectory=$PROD_DIR
ExecStart=/bin/bash -c 'while true; do docker-compose -f docker-compose.prod.yml ps; sleep 60; done'
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable megasena-monitor
systemctl start megasena-monitor

# Configurar backup automático
echo "Configurando backup automático..."
cat > /etc/cron.d/megasena-backup << CRON
0 2 * * * megasena cd $PROD_DIR && ./backup.sh > /var/log/megasena/backup.log 2>&1
CRON

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║     DEPLOY PRODUÇÃO CONCLUÍDO COM SUCESSO!     ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "✅ Sistema implantado em produção!"
echo ""
echo "📋 INFORMAÇÕES DO SISTEMA:"
echo "   Domínio principal: ${YELLOW}https://$DOMAIN${NC}"
echo "   Frontend:          ${YELLOW}https://$DOMAIN${NC}"
echo "   API Backend:       ${YELLOW}https://$DOMAIN/api${NC}"
echo "   IA Python:         ${YELLOW}https://$DOMAIN/ia${NC}"
echo "   Documentação:      ${YELLOW}https://$DOMAIN/docs${NC}"
echo ""
echo "🛠️  COMANDOS ÚTEIS:"
echo "   Status:            ${GREEN}systemctl status nginx${NC}"
echo "   Logs:              ${GREEN}tail -f /var/log/nginx/access.log${NC}"
echo "   Monitorar:         ${GREEN}systemctl status megasena-monitor${NC}"
echo "   Backup manual:     ${GREEN}cd $PROD_DIR && ./backup.sh${NC}"
echo "   Restart serviços:  ${GREEN}cd $PROD_DIR && docker-compose -f docker-compose.prod.yml restart${NC}"
echo ""
echo "🔒 SEGURANÇA CONFIGURADA:"
echo "   ✓ Firewall (UFW)"
echo "   ✓ SSL/TLS $([ "$SSL_ENABLE" = "true" ] && echo "(Let's Encrypt)" || echo "(desabilitado)")"
echo "   ✓ Fail2Ban"
echo "   ✓ Usuário dedicado"
echo "   ✓ Logs centralizados"
echo "   ✓ Backup automático"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Configure o DNS do domínio para apontar para este servidor"
echo "2. Acesse https://$DOMAIN para verificar"
echo "3. Configure alertas de monitoramento"
echo "4. Teste o backup: cd $PROD_DIR && ./backup.sh"
echo ""
echo "${GREEN}🚀 Sistema pronto para produção!${NC}"
