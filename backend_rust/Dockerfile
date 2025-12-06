FROM rust:latest as builder

# Instala dependências SSL e outras necessárias
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Variáveis para corrigir problemas de rede do Cargo
ENV CARGO_HTTP_MULTIPLEXING=false
ENV CARGO_HTTP_TIMEOUT=600    

# CORREÇÃO: Remover comentário da linha do WORKDIR
WORKDIR /usr/src/app

COPY . .

# Compilar
RUN cargo build --release

# Imagem final
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar binário
COPY --from=builder /usr/src/app/target/release/megasena_backend .

# Expor porta
EXPOSE 8080

# Comando
CMD ["./megasena_backend"]