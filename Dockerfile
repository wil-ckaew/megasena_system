FROM node:20-alpine

WORKDIR /app

# Copiar arquivos de configuração primeiro
COPY package.json package-lock.json* ./

# Instalar dependências de produção
RUN npm ci --only=production

# Copiar o restante do código
COPY . .

# Criar pastas essenciais se não existirem
RUN mkdir -p public app

# Garantir que globals.css existe
RUN if [ ! -f app/globals.css ]; then \
      echo "@tailwind base;" > app/globals.css && \
      echo "@tailwind components;" >> app/globals.css && \
      echo "@tailwind utilities;" >> app/globals.css; \
    fi

# Build da aplicação
RUN npm run build

# Expor porta
EXPOSE 3000

# Comando de inicialização
CMD ["npm", "start"]
