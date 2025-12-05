# Etapa de compilação
FROM rust:1.83 as builder
WORKDIR /usr/src/backend_rust
COPY . .
RUN cargo build --release

# Etapa de execução
FROM debian:bookworm-slim

# ✅ Corrige o erro "libssl.so.3"
RUN apt-get update && apt-get install -y \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /usr/src/backend_rust/target/release/backend_rust .
EXPOSE 8080
CMD ["./backend_rust"]
