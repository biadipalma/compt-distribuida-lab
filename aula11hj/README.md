# Serviço de Processamento de Arquivos com gRPC (Entrega 1: CompressPDF)

Servidor em C++ (gRPC + Ghostscript) e cliente em Python, executados em containers Docker.

## Estrutura

```
proto/file_processor.proto     contrato gRPC
server_cpp/                    servidor (server.cc, CMakeLists.txt, Dockerfile)
client_python/                 cliente (client.py, requirements.txt, Dockerfile)
docker-compose.yml
```

## Como executar

Na pasta raiz do projeto:

```bash
docker-compose up -d --build
docker ps    # confira os nomes dos containers
```

### Terminal 1: servidor

```bash
docker exec -it aula11hj-servidor-grpc-1 bash
cd server_cpp
rm -rf build && mkdir build && cd build
cmake ..
make
./server
```

O log é gravado em `server.log`, na pasta onde o `./server` foi executado (`server_cpp/build/`).

### Terminal 2: cliente

```bash
docker exec -it aula11hj-cliente-python-1 bash
cd client_python
python -m grpc_tools.protoc -I../proto --python_out=. --grpc_python_out=. ../proto/file_processor.proto
python3 client.py
```

Coloque um PDF chamado `aula10.pdf` em `client_python/`. A saída é `comprimido.pdf`.

## Testes de erro

- Arquivo inexistente: o cliente mostra o erro e nada chega ao servidor.
- Arquivo que não é PDF (ex.: `.txt` renomeado): o servidor registra FALHA no log e retorna `INTERNAL`.

Sempre que alterar o código: `docker-compose down` e `docker-compose up -d --build`.
