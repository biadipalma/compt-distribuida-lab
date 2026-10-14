# cliente.py
import grpc
import notas_pb2
import notas_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = notas_pb2_grpc.GerenciadorNotasStub(channel)
        
        print("--- 1. Adicionando Notas ---")
        res1 = stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(
            ra="123", cod_disciplina="CIC0001", ano=2025, semestre=2, nota=9.5
        ))
        print(f"Servidor: {res1.msg}")

        res2 = stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(
            ra="123", cod_disciplina="CIC0002", ano=2025, semestre=2, nota=7.0
        ))
        print(f"Servidor: {res2.msg}")

        print("\n--- 2. Calculando Média ---")
        media_response = stub.CalcularMedia(notas_pb2.AlunoRequest(ra="123"))
        if media_response.sucesso:
            print(f"Média do aluno 123: {media_response.media:.2f}")
        else:
            print(f"Erro ao calcular média: {media_response.msg_erro}")

        print("\n--- 3. Consultando Nota Específica (Unário) ---")
        consulta = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="123", cod_disciplina="CIC0001"))
        if consulta.sucesso:
            print(f"Disciplina: {consulta.nota.cod_disciplina} | Nota: {consulta.nota.nota}")
        else:
            print(f"Erro: {consulta.msg_erro}")

        # --- CHAMADA DO DESAFIO (STREAMING) ---
        print("\n--- 4. Listando todas as notas do aluno 123 (DESAFIO - Server Streaming) ---")
        try:
            notas_stream = stub.ListarNotasAluno(notas_pb2.AlunoRequest(ra="123"))
            for nota in notas_stream:
                print(f" -> Recebido do stream | Disciplina: {nota.cod_disciplina}, Ano: {nota.ano}/{nota.semestre}, Nota: {nota.nota}")
        except grpc.RpcError as e:
            print(f"Erro ao chamar ListarNotasAluno: {e.details()}")

if __name__ == '__main__':
    run()