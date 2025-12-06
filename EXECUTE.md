# 🚀 GUIA DE EXECUÇÃO RÁPIDA - MEGA-SENA AI

## 📦 PRIMEIRA EXECUÇÃO

### Opção 1: Instalação Automática (Recomendado)
```bash
# 1. Torne os scripts executáveis
chmod +x *.sh

# 2. Instale o sistema
./install.sh

# 3. Inicie o sistema
./start.sh start
Opção 2: Passo a Passo Manual
# 1. Construir imagens Docker
docker-compose build

# 2. Iniciar serviços
docker-compose up -d

# 3. Verificar status
docker-compose ps
🌐 ACESSO AO SISTEMA

Após iniciar, acesse:

    Frontend: http://localhost:3000

    Backend API: http://localhost:8080

    IA Python API: http://localhost:5001

    Documentação IA: http://localhost:5001/docs

🛠️ COMANDOS PRINCIPAIS
Usando Makefile (Recomendado)
bash
make start       # Iniciar sistema
make stop        # Parar sistema
make restart     # Reiniciar
make status      # Ver status
make logs        # Ver logs
make test        # Executar testes
make backup      # Criar backup
make monitor     # Monitorar sistema
make dev         # Modo desenvolvimento
Usando Scripts Diretamente
./start.sh start     # Iniciar
./start.sh stop      # Parar
./start.sh status    # Status
./start.sh logs      # Logs
./test.sh           # Testes
./backup.sh         # Backup
./monitor.sh        # Monitorar
🧪 TESTE RÁPIDO
Testar API
bash
# Health check
curl http://localhost:8080/health

# Gerar jogo
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"day": 15}'

# Análise IA
curl http://localhost:5001/api/analysis
Testar Frontend

Abra no navegador: http://localhost:3000

    Digite um dia (1-31)

    Clique em "Gerar Jogos"

    Veja os números gerados

🔧 SOLUÇÃO DE PROBLEMAS
Problema: Portas em uso
bash
# Verificar processos
sudo lsof -i :3000 :8080 :5001

# Parar processos
sudo kill -9 <PID>
Problema: Docker não inicia
bash
# Reiniciar Docker
sudo systemctl restart docker

# Limpar tudo
docker system prune -a

# Reconstruir
docker-compose build --no-cache
Problema: Erro no Python
bash
# Verificar dependências
cd ia_python
pip install -r requirements.txt

# Testar Python
python3 -c "import pandas; print('OK')"
Problema: Frontend não carrega
bash
# Limpar cache Next.js
cd frontend_nextjs
rm -rf .next node_modules
npm install
npm run build
📊 MONITORAMENTO
Ver logs em tempo real
bash
./start.sh logs
# ou
docker-compose logs -f
Monitorar sistema
bash
./monitor.sh
# Opção interativa com menu
Ver recursos
bash
docker stats
# ou
./monitor.sh --auto
💾 BACKUP & RESTORE
Criar backup
bash


./backup.sh
# Backup salvo em: backups/megasena_backup_YYYYMMDD_HHMMSS.tar.gz
Listar backups
ls -la backups/
Restaurar backup
bash
./restore.sh megasena_backup_20240101_120000.tar.gz
# ou
make restore BACKUP=megasena_backup_20240101_120000.tar.gz
🚀 DEPLOY PRODUÇÃO
Pré-requisitos

    Domínio configurado

    Acesso root/sudo

    Portas 80/443 abertas

Executar deploy
bash
sudo ./deploy-prod.sh seu-dominio.com admin@seu-dominio.com
Após deploy

    Configure DNS para apontar para seu servidor

    Acesse https://seu-dominio.com

    Configure backup automático

    Configure monitoramento

📈 COMANDOS AVANÇADOS
Atualizar sistema
bash
./start.sh update
# ou
git pull origin main
docker-compose build
docker-compose up -d
Modo desenvolvimento
bash
./start.sh dev
# Inicia todos os serviços localmente sem Docker
Testes completos
bash
./test.sh
# Executa suite completa de testes
Limpeza completa
bash
./start.sh clean
# Remove tudo: containers, imagens, volumes
⚡ ATALHOS ÚTEIS
Atalho	Comando	Descrição
🚀	make start	Iniciar tudo
🛑	make stop	Parar tudo
🔄	make restart	Reiniciar
📊	make status	Ver status
📝	make logs	Ver logs
🧪	make test	Executar testes
💾	make backup	Criar backup
👁️	make monitor	Monitorar
🛠️	make dev	Modo dev
🆘 SUPORTE
Verificar versões
bash
docker --version
docker-compose --version
node --version
python3 --version
Verificar serviços
bash
# Todos os serviços
docker-compose ps

# Logs específicos
docker logs megasena-backend
docker logs megasena-ia
docker logs megasena-frontend
Reiniciar serviço específico
bash
docker-compose restart backend
docker-compose restart ia
docker-compose restart frontend
📞 CONTATO/SUPORTE

Em caso de problemas:

    Verifique logs: ./start.sh logs

    Execute testes: ./test.sh

    Consulte este guia

    Verifique issues no GitHub

✅ Sistema pronto para uso!

Acesse http://localhost:3000 e comece a gerar jogos da Mega-Sena com IA!

🎰 Boa sorte (e boa matemática)!
