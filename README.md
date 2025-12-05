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

---

## 🚀 Quickstart

### Pré-requisitos
- **Docker** e **Docker Compose**
- Ou localmente: Node.js 18+, Rust 1.70+, Python 3.10+

### Iniciar com Docker Compose

```bash
cd /home/kimel/rust/megasena_system
docker compose up -d --build
```

**Serviços iniciados:**
- 🎨 Frontend: http://localhost:3000
- 🔧 Backend: http://localhost:8080
- 🤖 ML Service: http://localhost:5000

### Parar os serviços

```bash
docker compose down
```

---

## 📁 Estrutura do Projeto

```
megasena_system/
├── frontend_nextjs/              # Interface React + Next.js
│   ├── pages/
│   │   ├── index.js              # Página principal (elegante)
│   │   └── api/
│   │       └── generate.js        # Endpoint /api/generate
│   ├── components/
│   │   └── ApostasTable.js        # Componente de bolas numeradas
│   ├── styles/
│   │   └── globals.css            # Estilos globais + fonte
│   └── Dockerfile
│
├── backend_rust/                 # API REST em Rust
│   ├── src/
│   │   ├── main.rs               # Entrada principal
│   │   ├── routes.rs             # Definição de rotas
│   │   └── handlers/
│   │       └── megasena_handler.rs # Lógica da Mega Sena
│   ├── Cargo.toml
│   └── Dockerfile
│
├── ml_service/                   # Serviço de IA em Flask
│   ├── app.py                    # Aplicação Flask
│   ├── megasena_ai_v6.py         # Modelo de IA (v6)
│   ├── megasena_rf_model.joblib  # Modelo Random Forest treinado
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml            # Orquestração dos serviços
└── README.md                      # Este arquivo
```

---

## 🎯 Como Usar

### Via Interface Web (Recomendado)

1. Abra http://localhost:3000 no navegador
2. Digite um **dia (1–31)** no campo de entrada
3. Clique em **"Gerar Aposta"** ou pressione **Enter**
4. Visualize os **6 números sorteados** em bolas animadas

### Via API REST (cURL)

#### Gerar aposta para o dia 15:

```bash
curl "http://localhost:3000/api/generate?day=15"
```

**Resposta esperada:**
```json
{
  "generated_numbers": [7, 18, 25, 34, 42, 55],
  "raw": {
    "combinacoes_geradas": [...],
    "dia": 15,
    "jogos_sugeridos": [[...], ...],
    "previsao_modelo": [0, 1],
    "probabilidades": [...],
    "grafico_base64": "iVBORw0KGgo..."
  }
}
```

---

## 🎨 Design & UX

### Tema Visual
- **Fundo:** Gradiente suave azul-claro → lilás (leve e elegante)
- **Cards:** Efeito glassmorphism com backdrop blur
- **Botões:** Gradiente ouro com transições suaves
- **Input:** Texto escuro para máxima legibilidade
- **Fonte:** Poppins (Google Fonts)

### Animações
✨ Emoji flutuante no título  
🎯 Bolas numeradas com efeito brilho (shine)  
⬆️ Lift effect no hover dos botões  
🎪 Transições fluidas de entrada/saída

---

## 🛠️ Desenvolvimento

### Frontend (Next.js)

```bash
cd frontend_nextjs
npm install
npm run dev  # Desenvolvimento em http://localhost:3000
npm run build
npm start
```

### Backend (Rust)

```bash
cd backend_rust
cargo run  # Desenvolvimento em http://localhost:8080
cargo build --release
```

### ML Service (Flask)

```bash
cd ml_service
pip install -r requirements.txt
python app.py  # Desenvolvimento em http://localhost:5000
```

---

## 🤖 Modelo de IA

**Tipo:** Random Forest Classifier  
**Entrada:** Combinação de 6 números (1–60)  
**Saída:** Previsão binária + Probabilidades  
**Arquivo:** `ml_service/megasena_rf_model.joblib`

### Versões de IA disponíveis:
- `megasena_ai_v2.py` - Versão inicial
- `megasena_ai_v3.py` - Melhorias v3
- `megasena_ai_v4.py` - Aprimoramentos v4
- `megasena_ai_v5.py` - Otimizações v5
- `megasena_ai_v6.py` - Versão atual (mais precisa)

---

## 📊 Endpoints da API

### Next.js API Route

| Endpoint | Método | Parâmetros | Retorno |
|----------|--------|-----------|---------|
| `/api/generate` | GET | `day` (1–31) | `{ generated_numbers, raw }` |

### Backend Rust (8080)

Consultar `backend_rust/src/routes.rs` para endpoints adicionais.

### ML Service Flask (5000)

| Endpoint | Método | Body | Retorno |
|----------|--------|------|---------|
| `/predict` | POST | `{ "dia": int }` | JSON com números e gráfico |

---

## 🔧 Configuração

### Variáveis de Ambiente

**Frontend (`.env.local` ou Docker):**
```env
NEXT_PUBLIC_API_ML=http://ml_service:5000
```

**Backend (`.env`):**
```env
DATABASE_URL=postgres://user:pass@db:5432/backend_db
FLASK_ENV=production
```

**Docker Compose:**
Consulte `docker-compose.yml` para todas as variáveis.

---

## 📦 Dependências Principais

### Frontend
- **Next.js** 13.5.6
- **React** 18.2.0
- **Poppins Font** (Google Fonts)

### Backend
- **Actix-web** (Rust)
- **PostgreSQL 15**

### ML Service
- **Flask**
- **scikit-learn** (Random Forest)
- **NumPy, Pandas**
- **Matplotlib** (Gráficos)

---

## 🐛 Troubleshooting

### "Erro ao gerar aposta: fetch failed"
**Solução:** Verificar se o serviço ML está rodando:
```bash
docker compose logs ml_service
```

### Input não está visível
**Solução:** Cores ajustadas para contraste. Se ainda tiver problemas:
```bash
docker compose up -d --build frontend
```

### Porta já em uso
```bash
# Alterar porta no docker-compose.yml:
ports:
  - "3001:3000"  # Novo: 3001
```

---

## 📝 Licença

MIT License - Sinta-se livre para usar, modificar e distribuir.

---

## 👨‍💻 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📧 Contato & Suporte

Para dúvidas, abra uma **Issue** no repositório ou entre em contato.

---

## 🎓 Aprendizados

Este projeto demonstra:
- ✅ Arquitetura **microserviços** com Docker
- ✅ Frontend moderno com **Next.js** e **React Hooks**
- ✅ Backend robusto em **Rust** com **Actix-web**
- ✅ Integração de **Machine Learning** em produção
- ✅ Design responsivo e acessível com **CSS puro**
- ✅ Orquestração com **Docker Compose**

---

**Feito com ❤️ e ☕**

Última atualização: **5 de dezembro de 2025**
