# servidor.py
import grpc
from concurrent import futures
import notas_pb2
import notas_pb2_grpc

# Armazenamento em memória (simulando um banco de dados)
# Ex: { "123_DISC1": Nota(...), "123_DISC2": Nota(...) }
db_notas = {}

class GerenciadorNotasServicer(notas_pb2_grpc.GerenciadorNotasServicer):
    
    def AdicionarNota(self, request, context):
        print(f"[ADD] Adicionando nota para RA {request.ra} na disciplina {request.cod_disciplina}")
        chave = f"{request.ra}_{request.cod_disciplina}"
        
        if chave in db_notas:
            return notas_pb2.StatusResponse(
                sucesso=False, 
                msg="Nota já existe para este aluno/disciplina. Use AlterarNota."
            )
        
        # Cria e armazena o objeto Nota
        nova_nota = notas_pb2.Nota(
            ra=request.ra,
            cod_disciplina=request.cod_disciplina,
            ano=request.ano,
            semestre=request.semestre,
            nota=request.nota
        )
        db_notas[chave] = nova_nota
        return notas_pb2.StatusResponse(sucesso=True, msg="Nota adicionada com sucesso!")

    def AlterarNota(self, request, context):
        print(f"[ALT] Alterando nota para RA {request.ra} na disciplina {request.cod_disciplina}")
        chave = f"{request.ra}_{request.cod_disciplina}"
        
        if chave not in db_notas:
            return notas_pb2.StatusResponse(
                sucesso=False, 
                msg="Nota não encontrada para este aluno/disciplina. Use AdicionarNota."
            )
        
        # Atualiza o objeto Nota
        db_notas[chave].ano = request.ano
        db_notas[chave].semestre = request.semestre
        db_notas[chave].nota = request.nota
        
        return notas_pb2.StatusResponse(sucesso=True, msg="Nota alterada com sucesso!")

    def ConsultarNota(self, request, context):
        print(f"[CONS] Consultando nota para RA {request.ra} na disciplina {request.cod_disciplina}")
        chave = f"{request.ra}_{request.cod_disciplina}"
        
        if chave not in db_notas:
            return notas_pb2.ConsultaNotaResponse(
                sucesso=False,
                msg_erro="Nota não encontrada."
            )
        
        return notas_pb2.ConsultaNotaResponse(
            sucesso=True,
            nota=db_notas[chave]
        )

    def CalcularMedia(self, request, context):
        print(f"[MEDIA] Calculando média para o RA {request.ra}")
        
        # Filtra as notas do aluno correspondente ao RA
        notas_aluno = [n.nota for n in db_notas.values() if n.ra == request.ra]
        
        if not notas_aluno:
            return notas_pb2.MediaResponse(
                sucesso=False,
                msg_erro="Nenhuma nota encontrada para este aluno."
            )
        
        media = sum(notas_aluno) / len(notas_aluno)
        return notas_pb2.MediaResponse(
            sucesso=True,
            media=media
        )

    # --- IMPLEMENTAÇÃO DO DESAFIO (SERVER STREAMING) ---
    def ListarNotasAluno(self, request, context):
        print(f"[STREAM] Listando notas via Server-Side Streaming para o RA {request.ra}")
        

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notas_pb2_grpc.add_GerenciadorNotasServicer_to_server(GerenciadorNotasServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC rodando na porta 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()