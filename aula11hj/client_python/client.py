import os
import grpc
import file_processor_pb2
import file_processor_pb2_grpc

# ==============================================================================
# CONFIGURAÇÃO DE REDE (NÃO ALTERAR)
# Desliga a interferência do proxy do Codespaces na rede interna do Docker
# ==============================================================================
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['no_proxy'] = '*'

# ==============================================================================
# MÉTODOS AUXILIARES FORNECIDOS (NÃO ALTERAR)
# ==============================================================================
def generate_requests(file_path, request_params):
    file_name = os.path.basename(file_path)
    # Envia os parâmetros na primeira mensagem
    yield file_processor_pb2.FileRequest(file_name=file_name, **request_params)

    # Faz o stream dos bytes nas mensagens seguintes
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            yield file_processor_pb2.FileRequest(
                file_content=file_processor_pb2.FileChunk(content=chunk)
            )

def save_response_stream(response_stream, output_path):
    with open(output_path, 'wb') as f:
        for response in response_stream:
            if response.HasField('file_content'):
                f.write(response.file_content.content)
    return True

# ==============================================================================
# CLASSE DO CLIENTE gRPC
# ==============================================================================
class FileProcessorClient:
    def __init__(self, target='servidor-grpc:50051'):
        # Canal configurado para ignorar proxy e usar texto plano (sem SSL)
        self.channel = grpc.insecure_channel(
            target,
            options=[('grpc.enable_http_proxy', 0)]
        )
        self.stub = file_processor_pb2_grpc.FileProcessorServiceStub(self.channel)

    # ==========================================================================
    # IMPLEMENTAÇÃO SUA
    # ==========================================================================
    def compress_pdf(self, input_path, output_path):
        """Envia um PDF ao servidor, recebe a versão comprimida e salva em output_path."""
        # 1. Parâmetros: indica a requisição CompressPDFRequest (campo do oneof)
        params = {'compress_pdf_params': file_processor_pb2.CompressPDFRequest()}

        # 2. Iterador que gera o stream de requisições
        requests = generate_requests(input_path, params)

        # 3. Chamada ao método do stub (retorna o stream de respostas)
        response_stream = self.stub.CompressPDF(requests)

        # 4. Salva o arquivo final e retorna o resultado
        return save_response_stream(response_stream, output_path)

    # ==========================================================================
    # MÉTODOS IGNORADOS PARA ESTA ENTREGA
    # ==========================================================================
    def convert_to_txt(self, input_path, output_path):
        # Não é necessário implementar para esta atividade.
        pass

    def convert_image(self, input_path, output_path, out_fmt):
        # Não é necessário implementar para esta atividade.
        pass

    def resize_image(self, input_path, output_path, w, h):
        # Não é necessário implementar para esta atividade.
        pass

# ==============================================================================
# ÁREA DE TESTE (PODE ALTERAR OS CAMINHOS DOS ARQUIVOS)
# ==============================================================================
if __name__ == '__main__':
    # Conecta no servidor usando as definições do compose
    cliente = FileProcessorClient(target='localhost:50051')
    # O padrão seria algo tipo
    # cliente = FileProcessorClient(target='servidor-grpc:50051')
    # mas usamos o host.... para contornar problemas de conexão (timeout) do codespaces
    # para teste no host do codespaces
    # cliente = FileProcessorClient(target='localhost:50051')

    print("Iniciando compressão...")

    # IMPORTANTE: O arquivo de origem precisa existir na pasta indicada.
    try:
        cliente.compress_pdf('aula10.pdf', 'comprimido.pdf')
        print("Compressão finalizada! Verifique o arquivo comprimido.pdf na sua pasta.")
    except grpc.RpcError as e:
        print(f"Erro do servidor: {e.code().name} - {e.details()}")
    except Exception as e:
        print(f"Erro durante a execução: {e}")
