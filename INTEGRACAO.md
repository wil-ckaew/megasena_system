# 🤖 Integração Chatbot + Bolão Mega-Sena

## 🎯 Funcionalidades Adicionadas

### 1. **Chatbot Inteligente**
- API REST completa com FastAPI
- WebSocket para comunicação em tempo real
- Detecção de intenções com ML
- Respostas contextualizadas
- Histórico de conversas

### 2. **Sistema de Bolão Otimizado**
- Geração de múltiplos jogos com IA
- Maximização de cobertura numérica
- Análise estatística em tempo real
- Histórico de boloes gerados
- Exportação para CSV

### 3. **Aprendizado de Máquina**
- Modelo RandomForest treinado com dados históricos
- Análise de similaridade com sorteios vencedores
- Previsão de probabilidades
- Atualização contínua do modelo

### 4. **Interface Web Moderna**
- Painel de controle de bolão
- Gráficos interativos
- Análise detalhada de jogos
- Gerenciamento de orçamento

## 🚀 Como Integrar com seu Sistema

### Passo 1: Adicionar dependências
```bash
# No seu frontend Next.js
npm install @mui/material @emotion/react @emotion/styled
npm install recharts
Passo 2: Configurar variáveis de ambiente
# .env.local no frontend
NEXT_PUBLIC_CHATBOT_API=http://localhost:8000
NEXT_PUBLIC_ML_API=http://localhost:5001
Passo 3: Rotas adicionadas
GET    /api/estatisticas          # Estatísticas atualizadas
POST   /api/chat                  # Enviar mensagem ao chatbot
POST   /api/analisar              # Analisar jogo específico
POST   /api/bolao                 # Gerar bolão otimizado
GET    /api/historico_boloes      # Histórico de boloes
WS     /ws/chat                   # WebSocket para chat em tempo real
Passo 4: Componentes React adicionados

    app/bolao/page.tsx - Painel completo de bolão

    app/chatbot/page.tsx - Interface de chat

    components/GameAnalysis.tsx - Componente de análise

    components/BolaoStats.tsx - Estatísticas de bolão

🔗 Integração com Backend Rust
API endpoints do Rust que podem ser consumidos:
// Exemplo de chamada para o chatbot
pub async fn consultar_chatbot(mensagem: String) -> Result<ChatbotResponse> {
    let client = reqwest::Client::new();
    let response = client
        .post("http://chatbot-service:8000/api/chat")
        .json(&ChatbotRequest { text: mensagem })
        .send()
        .await?;
    
    Ok(response.json().await?)
}

// Exemplo para gerar bolão
pub async fn gerar_bolao(quantidade: usize) -> Result<BolaoResponse> {
    let response = reqwest::Client::new()
        .post("http://chatbot-service:8000/api/bolao")
        .json(&BolaoRequest { 
            quantidade_jogos: quantidade,
            metodo: "optimized".to_string(),
            incluir_historico: true 
        })
        .send()
        .await?;
    
    Ok(response.json().await?)
}
📊 Fluxo de Dados
Usuário → Frontend Next.js → Chatbot API → ML Service
     ↓         ↓                 ↓            ↓
Interface  Componentes      Processamento  Análise IA
  Web      React           Mensagens      Modelos ML
     ↓         ↓                 ↓            ↓
Backend  ← Histórico  ←  Respostas   ←  Resultados
  Rust      Chat          Chatbot        Análise
🐳 Docker Compose Atualizado

Seu docker-compose.yml agora inclui:
services:
  ml-service:       # Serviço ML existente
  chatbot-service:  # Novo serviço de chatbot
  frontend:         # Frontend Next.js com novas páginas
  backend:          # Backend Rust atualizado
🧪 Testando a Integração
# 1. Iniciar todos serviços
./integracao_chatbot.sh

# 2. Testar API do chatbot
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Gerar um jogo otimizado"}'

# 3. Testar geração de bolão
curl -X POST http://localhost:8000/api/bolao \
  -H "Content-Type: application/json" \
  -d '{"quantidade_jogos": 5}'

# 4. Acessar interface web
# http://localhost:3000/bolao
# http://localhost:3000/chatbot
🔧 Configurações Avançadas
Treinamento do modelo:
python
# Treinar modelo com mais dados
curl -X GET http://localhost:8000/api/treinar_modelo

# Monitorar acurácia
curl -X GET http://localhost:8000/api/modelo/status
Personalização:

    Edite ml_service/chatbot_service.py para adicionar novas intenções

    Modifique frontend_nextjs/app/bolao/page.tsx para customizar UI

    Ajuste parâmetros do modelo em MegaSenaChatbot.inicializar_modelo_ia()

📈 Monitoramento
Logs:

# Ver logs do chatbot
docker logs megasena_system-chatbot-service-1

# Ver logs do frontend
docker logs megasena_system-frontend-1
Métricas:

    Acesse http://localhost:8000/docs para documentação API

    Use http://localhost:3000/_next/insights para métricas Next.js

⚠️ Solução de Problemas
Problema: Chatbot não responde

# Verificar se o serviço está rodando
curl http://localhost:8000

# Reiniciar serviço
docker-compose restart chatbot-service
Problema: Modelo não treina

# Verificar dados históricos
wc -l resultados_megasena.csv

# Forçar treinamento
curl -X GET http://localhost:8000/api/treinar_modelo
Problema: Frontend não carrega
# Verificar build
cd frontend_nextjs && npm run build

# Limpar cache
rm -rf .next && npm run dev
🚀 Próximos Passos

    Adicionar autenticação para múltiplos usuários

    Implementar cache para respostas do chatbot

    Adicionar mais modelos de machine learning

    Integrar com APIs de resultados em tempo real

    Criar dashboard administrativo

Sistema integrado e pronto para produção! 🎉

O chatbot agora:

    ✅ Aprende com resultados históricos

    ✅ Gera boloes otimizados

    ✅ Integra com seu sistema existente

    ✅ Fornece interface web moderna

    ✅ Escalável com Docker

Boa sorte com as apostas! 🍀
