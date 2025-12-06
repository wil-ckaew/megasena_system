FROM node:20

WORKDIR /app

# Copiar apenas os arquivos de dependências primeiro
COPY package.json package-lock.json* ./
COPY next.config.js ./

# Instalar dependências
RUN npm install

# Copiar o restante do código
COPY . .

# Construir a aplicação
RUN npm run build

# Expor porta
EXPOSE 3000

# Comando para iniciar
CMD ["npm", "start"]
