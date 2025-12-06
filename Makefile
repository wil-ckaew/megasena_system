.PHONY: help start stop restart status logs build clean dev test update backup restore monitor deploy

# Cores
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=20

# Ajuda
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

## Iniciar todos os serviços com Docker
start: 
	@echo "${GREEN}Iniciando sistema MegaSena AI...${RESET}"
	@./start.sh start

## Parar todos os serviços
stop:
	@echo "${YELLOW}Parando serviços...${RESET}"
	@./start.sh stop

## Reiniciar serviços
restart:
	@echo "${YELLOW}Reiniciando serviços...${RESET}"
	@./start.sh restart

## Mostrar status dos serviços
status:
	@./start.sh status

## Monitorar logs em tempo real
logs:
	@./start.sh logs

## Construir imagens Docker
build:
	@echo "${GREEN}Construindo imagens Docker...${RESET}"
	@./start.sh build

## Limpar ambiente Docker completamente
clean:
	@echo "${YELLOW}Limpando ambiente Docker...${RESET}"
	@./start.sh clean

## Modo desenvolvimento (local sem Docker)
dev:
	@echo "${GREEN}Iniciando modo desenvolvimento...${RESET}"
	@./start.sh dev

## Executar testes do sistema
test:
	@echo "${GREEN}Executando testes...${RESET}"
	@./test.sh

## Atualizar código e reiniciar
update:
	@echo "${GREEN}Atualizando sistema...${RESET}"
	@./start.sh update

## Criar backup do sistema
backup:
	@echo "${GREEN}Criando backup...${RESET}"
	@./backup.sh

## Restaurar sistema de backup
restore:
	@echo "${YELLOW}Restaurando sistema...${RESET}"
	@if [ -z "$(BACKUP)" ]; then \
		echo "${RED}Especifique o backup: make restore BACKUP=<arquivo>${RESET}"; \
		echo "Backups disponíveis:"; \
		ls -la backups/*.tar.gz 2>/dev/null || echo "  (nenhum backup)"; \
		exit 1; \
	fi; \
	./restore.sh "$(BACKUP)"

## Monitorar sistema
monitor:
	@echo "${GREEN}Iniciando monitoramento...${RESET}"
	@./monitor.sh

## Deploy em produção
deploy:
	@echo "${GREEN}Preparando deploy em produção...${RESET}"
	@if [ -z "$(DOMAIN)" ] || [ -z "$(EMAIL)" ]; then \
		echo "${RED}Use: make deploy DOMAIN=exemplo.com EMAIL=admin@exemplo.com${RESET}"; \
		exit 1; \
	fi; \
	./deploy-prod.sh "$(DOMAIN)" "$(EMAIL)"

## Instalar sistema
install:
	@echo "${GREEN}Instalando sistema...${RESET}"
	@./install.sh

## Verificar saúde da API
health:
	@echo "${GREEN}Verificando saúde da API...${RESET}"
	@curl -s http://localhost:8080/health | jq . || curl -s http://localhost:8080/health

## Gerar jogo de teste
generate:
	@echo "${GREEN}Gerando jogo de teste...${RESET}"
	@curl -X POST http://localhost:8080/api/generate \
		-H "Content-Type: application/json" \
		-d '{"day": 15}' | jq '.games[0]'

## Ver análise da IA
analysis:
	@echo "${GREEN}Obtendo análise da IA...${RESET}"
	@curl -s http://localhost:5001/api/analysis | jq '.hot_numbers'

## Listar backups disponíveis
list-backups:
	@echo "${GREEN}Backups disponíveis:${RESET}"
	@ls -lh backups/*.tar.gz 2>/dev/null || echo "  (nenhum backup)"

## Limpar logs antigos
clean-logs:
	@echo "${YELLOW}Limpando logs antigos...${RESET}"
	@find . -name "*.log" -mtime +7 -delete
	@find logs/ -type f -mtime +7 -delete 2>/dev/null || true
	@echo "${GREEN}Logs limpos${RESET}"

## Estatísticas do sistema
stats:
	@echo "${GREEN}Estatísticas do sistema:${RESET}"
	@echo "Containers: $$(docker ps -q | wc -l)"
	@echo "Imagens: $$(docker images -q | wc -l)"
	@echo "Volumes: $$(docker volume ls -q | wc -l)"
	@echo "Backups: $$(ls backups/*.tar.gz 2>/dev/null | wc -l)"
	@echo "Logs: $$(find . -name "*.log" -type f | wc -l)"

## Versão do sistema
version:
	@echo "${GREEN}MegaSena AI FullStack v1.0.0${RESET}"
	@echo "Backend: Rust + Actix-web"
	@echo "IA: Python + FastAPI"
	@echo "Frontend: Next.js + React"
	@echo "Orquestração: Docker Compose"

## Ajuda detalhada
help-all:
	@echo "${GREEN}COMANDOS DISPONÍVEIS:${RESET}"
	@echo ""
	@echo "${YELLOW}Gerenciamento básico:${RESET}"
	@echo "  make start        - Iniciar sistema"
	@echo "  make stop         - Parar sistema"
	@echo "  make restart      - Reiniciar"
	@echo "  make status       - Ver status"
	@echo "  make logs         - Ver logs"
	@echo ""
	@echo "${YELLOW}Desenvolvimento:${RESET}"
	@echo "  make dev          - Modo desenvolvimento"
	@echo "  make build        - Construir imagens"
	@echo "  make test         - Executar testes"
	@echo "  make update       - Atualizar sistema"
	@echo ""
	@echo "${YELLOW}Backup/restore:${RESET}"
	@echo "  make backup       - Criar backup"
	@echo "  make restore      - Restaurar backup"
	@echo "  make list-backups - Listar backups"
	@echo ""
	@echo "${YELLOW}Monitoramento:${RESET}"
	@echo "  make monitor      - Monitorar sistema"
	@echo "  make health       - Verificar saúde"
	@echo "  make stats        - Estatísticas"
	@echo ""
	@echo "${YELLOW}Deploy:${RESET}"
	@echo "  make deploy       - Deploy em produção"
	@echo "  make install      - Instalar sistema"
	@echo ""
	@echo "${YELLOW}Utilitários:${RESET}"
	@echo "  make generate     - Gerar jogo teste"
	@echo "  make analysis     - Análise da IA"
	@echo "  make clean        - Limpar tudo"
	@echo "  make clean-logs   - Limpar logs"
	@echo "  make version      - Ver versão"
	@echo ""
	@echo "${GREEN}Exemplos:${RESET}"
	@echo "  make start                     # Iniciar sistema"
	@echo "  make restore BACKUP=backup.tar.gz # Restaurar"
	@echo "  make deploy DOMAIN=ex.com EMAIL=admin@ex.com"
