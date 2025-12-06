# MegaSena AI - Sistema Inteligente de Geração de Apostas 🎰

Um sistema completo de geração de apostas para a Mega Sena, combinando **Machine Learning**, **API REST em Rust** e **Interface Next.js moderna e elegante**.

---

## 📋 Visão Geral

O **MegaSena AI** é um projeto fullstack que utiliza análise de padrões históricos e IA para sugerir combinações de números para apostas na Mega Sena, baseando-se no dia do mês inserido pelo usuário.

### Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Next.js (3000)                  │
│              UI elegante com gradientes e animações         │
└────────────────────────────┬────────────────────────────────┘
                             │
                    API Route: /api/generate
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
┌───────▼──────────────┐           ┌────────────▼─────────────┐
│ Backend Rust (8080)  │           │  ML Service Flask (5000) │
│  - Rotas API         │           │  - Modelo RF             │
│  - Lógica principal  │           │  - Previsões             │
└──────────────────────┘           │  - Probabilidades        │
                                   └──────────────────────────┘
```
# ============================================
# 6. README COMPLETO
# ============================================

cat > ~/rust/megasena_system/README.md << 'EOF'
# 🎰 MegaSena AI - Sistema FullStack Inteligente

Sistema completo para geração otimizada de jogos da Mega-Sena, combinando:

- **🦀 Backend Rust**: API Gateway e lógica de negócios
- **🤖 IA Python**: Machine Learning e análise estatística
- **⚛️ Frontend Next.js**: Interface web moderna e responsiva

## 🚀 Começo Rápido

### Opção 1: Docker (Recomendado)

```bash
# 1. Clone/baixe o projeto e navegue até ele
cd megasena_system

# 2. Torne o script executável
chmod +x start.sh

# 3. Inicie todos os serviços
./start.sh start

# 4. Acesse:
#    Frontend: http://localhost:3000
#    Backend Rust: http://localhost:8080
#    IA Python: http://localhost:5001/docs

Opção 2: Desenvolvimento Local
bash

# Execute o modo desenvolvimento
./start.sh dev

📁 Estrutura do Projeto
text

megasena_system/
├── backend_rust/          # Backend em Rust (Actix-web)
│   ├── src/
│   ├── Cargo.toml
│   └── Dockerfile
├── ia_python/            # IA em Python (FastAPI)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend_nextjs/      # Frontend em Next.js
│   ├── pages/
│   ├── components/
│   ├── styles/
│   └── Dockerfile
├── resultados_megasena.csv  # Dados históricos
├── docker-compose.yml    # Orquestração Docker
├── start.sh             # Script de controle
└── README.md           # Esta documentação

🛠️ Serviços e Portas
Serviço	Porta	Descrição	URL
Frontend Next.js	3000	Interface web	http://localhost:3000
Backend Rust	8080	API Gateway	http://localhost:8080
IA Python	5001	Machine Learning	http://localhost:5001/docs
🔧 Arquitetura do Sistema
text

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │◄──►│   Backend       │◄──►│   IA Python     │
│   Next.js       │    │   Rust          │    │   FastAPI       │
│   (React)       │    │   (Actix-web)   │    │   (ML/Stats)    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
   Interface Web          Lógica Negócios      Análise de Dados
   Usuário Final          Validações           Machine Learning
   Experiência UX         Fallback Rust        Estatística

🎯 Funcionalidades
Backend Rust

    ✅ API RESTful com Actix-web

    ✅ Validação de dados de entrada

    ✅ Sistema de fallback inteligente

    ✅ Logging estruturado

    ✅ Health checks

    ✅ CORS configurado

IA Python

    ✅ Análise de dados históricos CSV

    ✅ 4 métodos de geração:

        Método Caravaca (baseado no dia)

        Método Estatístico (frequência)

        Método IA (machine learning)

        Método Híbrido (recomendado)

    ✅ API documentada com Swagger/OpenAPI

    ✅ Cache inteligente de dados

Frontend Next.js

    ✅ Interface moderna com Tailwind CSS

    ✅ Animações com Framer Motion

    ✅ Geração em tempo real

    ✅ Estatísticas visuais

    ✅ Responsivo (mobile/desktop)

    ✅ Notificações toast

📊 Fluxo de Geração

    Usuário seleciona um dia (1-31) no frontend

    Frontend envia requisição para Backend Rust

    Backend Rust tenta chamar IA Python

    IA Python analisa dados e gera jogos otimizados

    Backend Rust recebe resposta ou usa fallback

    Frontend exibe jogos com estatísticas

🐳 Comandos Docker
bash

# Iniciar todos os serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Ver logs
docker-compose logs -f

# Reconstruir e iniciar
docker-compose up -d --build

# Ver status
docker-compose ps

🔄 Script de Controle

O script start.sh fornece controle completo:
bash

./start.sh start      # Iniciar todos os serviços
./start.sh stop       # Parar serviços
./start.sh restart    # Reiniciar serviços
./start.sh clean      # Limpar completamente
./start.sh dev        # Modo desenvolvimento
./start.sh status     # Verificar status
./start.sh logs       # Ver logs em tempo real
./start.sh build      # Reconstruir imagens

🧪 Testando a API
bash

# Testar Backend Rust
curl http://localhost:8080/health

# Testar IA Python
curl http://localhost:5001/health

# Gerar jogos via API
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"day": 15}' \
  | python3 -m json.tool

📈 Métodos de Geração
1. Método Caravaca

    Baseado no dia do mês

    Algoritmo determinístico

    Bom para padrões simples

2. Método Estatístico

    Análise de frequência histórica

    Considera números quentes/frios

    Baseado em probabilidade

3. Método IA

    Machine Learning simples

    Padrões complexos

    Aprendizado de dados

4. Método Híbrido (⭐ RECOMENDADO)

    Combina todos os métodos

    Maior diversificação

    Melhores resultados

🔒 Variáveis de Ambiente
Backend Rust (.env)
env

HOST=0.0.0.0
PORT=8080
RUST_LOG=info
PYTHON_IA_URL=http://ia_python:5001/api/generate

IA Python (.env)
env

HOST=0.0.0.0
PORT=5001
DEBUG=False
CSV_PATH=../resultados_megasena.csv

Frontend Next.js (.env.local)
env

BACKEND_URL=http://localhost:8080
PYTHON_IA_URL=http://localhost:5001

🐛 Solução de Problemas
Problema: Portas já em uso
bash

# Verificar processos nas portas
sudo lsof -i :3000 :8080 :5001

# Matar processos se necessário
sudo kill -9 <PID>

Problema: Docker build falha
bash

# Limpar cache Docker
docker system prune -a

# Reconstruir
./start.sh clean
./start.sh build

Problema: CSV não encontrado
bash

# Verificar se o arquivo existe
ls -la resultados_megasena.csv

# Copiar exemplo se necessário
cp exemplo.csv resultados_megasena.csv

📝 Formato do CSV

O sistema espera um CSV com colunas:
text

n1,n2,n3,n4,n5,n6
1,2,3,4,5,6
7,8,9,10,11,12
...

🔮 Roadmap Futuro

    Treinamento de modelo de deep learning

    Sistema de recomendação personalizado

    Dashboard administrativo

    API GraphQL

    Cache Redis

    Autenticação JWT

    Deploy na nuvem (AWS/GCP)

⚠️ Aviso Legal

ATENÇÃO: Este sistema é para fins educacionais e de pesquisa. Não garantimos ganhos em loterias. O jogo deve ser feito com responsabilidade. Consulte as leis da sua região sobre jogos de azar.
📄 Licença

Projeto educacional - Use com responsabilidade.
👥 Contribuição

    Fork o projeto

    Crie sua branch (git checkout -b feature/nova-funcionalidade)

    Commit suas mudanças (git commit -m 'Add nova funcionalidade')

    Push para a branch (git push origin feature/nova-funcionalidade)

    Abra um Pull Request

✨ Créditos

Desenvolvido com:

    🦀 Rust + Actix-web

    🐍 Python + FastAPI + scikit-learn

    ⚛️ Next.js + React + Tailwind CSS

    🐳 Docker + Docker Compose

🎰 Que a sorte esteja com você (mas a matemática ajuda mais)!
EOF
============================================
7. ARQUIVOS DE CONFIGURAÇÃO EXTRAS
============================================
Gitignore

cat > ~/rust/megasena_system/.gitignore << 'EOF'
Dependencies

node_modules/
**/target/
**/pycache/
**/*.pyc
**/venv/
**/.env
**/.env.local
Build outputs

**/dist/
**/build/
**/.next/
**/out/
IDE

.vscode/
.idea/
*.swp
*.swo
Logs

*.log
logs/
OS

.DS_Store
Thumbs.db
Docker

*.tar.gz
