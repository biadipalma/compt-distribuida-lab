FROM ubuntu:22.04

# Evitar prompts interativos durante a instalação do apt
ENV DEBIAN_FRONTEND=noninteractive

# Atualizar pacotes e instalar todas as dependências do servidor
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    ghostscript \
    poppler-utils \
    imagemagick \
    libgrpc++-dev \
    libprotobuf-dev \
    protobuf-compiler-grpc \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Permissões do ImageMagick para leitura/escrita de PDFs (conversões extras)
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/g' /etc/ImageMagick-6/policy.xml || true

WORKDIR /workspace
