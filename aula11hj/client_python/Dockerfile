FROM python:3.10-slim

# Instalar dependências básicas do sistema
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copiar os requisitos do Python
COPY client_python/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
