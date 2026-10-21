# Relatório — Serviço de Processamento de Arquivos com gRPC (Entrega 1: CompressPDF)

## 1. Visão geral
Serviço gRPC em que um cliente Python envia um PDF em streaming para um servidor C++. O servidor comprime o arquivo com o Ghostscript (`gs`) e devolve o resultado, também em streaming. Toda a solução roda em containers Docker (servidor e cliente em containers separados, orquestrados pelo `docker-compose`).

## 2. Implementação
**Protobuf.** `FileProcessorService` com quatro RPCs bidirecionais com streaming (`CompressPDF`, `ConvertToTXT`, `ConvertImageFormat`, `ResizeImage`). O arquivo trafega em `FileChunk` de 1 KB; a primeira mensagem carrega o nome do arquivo e os parâmetros (`oneof parameters`).

**Servidor (C++).**
- `CompressPDF`: recebe o arquivo (`ReceiveFile`) em `/tmp`, executa `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook ...` via `std::system`, verifica o código de retorno e se a saída existe, devolve o resultado (`SendFile`) e remove os temporários.
- `LogOperation`: grava em `server.log` (modo append) timestamp, tipo (INICIO/SUCESSO/FALHA), serviço, nome do arquivo e mensagem.
- Erros: `INVALID_ARGUMENT` (nada recebido ou nome inválido) e `INTERNAL` (falha do Ghostscript).

**Cliente (Python).** `compress_pdf` monta os parâmetros (`CompressPDFRequest`), usa `generate_requests` para enviar em stream, chama `stub.CompressPDF` e grava a resposta com `save_response_stream`. Erros gRPC são tratados no `main`.

**Containers.** Imagem do servidor: Ubuntu 22.04 com gRPC, protobuf, Ghostscript, Poppler e ImageMagick. Imagem do cliente: Python 3.10-slim com `grpcio` e `grpcio-tools`. O compose monta o projeto em `/workspace` nos dois containers e expõe a porta 50051.

## 3. Decisões de design
- Streaming bidirecional para não carregar arquivos inteiros na memória.
- Chunks de 1 KB (definido nos auxiliares fornecidos).
- Validação do nome do arquivo (`SafeName`) antes de montá-lo no comando de shell, para evitar injeção de comandos.
- Verificação do arquivo de saída além do código de retorno do `gs`.
- Compilação manual dentro do container (roteiro do professor), com o CMake usando `pkg-config` no Ubuntu.

## 4. Desafios encontrados
- (Preencher: ex.: erro do `build/generated` ao compilar no Dockerfile; ajuste do CMake e do compose; nomes dos containers.)

## 5. Testes e prints
- [ ] Print: servidor iniciado ("Servidor gRPC operacional em 0.0.0.0:50051")
- [ ] Print: cliente com compressão bem-sucedida
- [ ] Print: `ls -lh` comparando `aula10.pdf` e `comprimido.pdf`
- [ ] Print: arquivo inexistente
- [ ] Print: arquivo inválido (.txt renomeado para .pdf)
- [ ] Print/arquivo: `server.log`

## 6. Segurança (observação)
Nomes de arquivo recebidos do cliente são validados antes do uso em comandos. O auxiliar `ReceiveFile` fornecido monta o caminho de entrada com o nome cru, o que em produção permitiria path traversal; em um cenário real, a sanitização deveria ocorrer antes de qualquer escrita em disco. Também não há autenticação nem TLS (canal inseguro, apenas para fins didáticos).
