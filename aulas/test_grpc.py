#pip install pytest
#pytest test_grpc.py -v

import pytest
import grpc
from concurrent import futures
import notas_pb2
import notas_pb2_grpc
import servidor # Importa o servidor.py implementado pelo aluno

@pytest.fixture(scope="module")
def grpc_server():
    """Inicializa o servidor gRPC localmente para os testes."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notas_pb2_grpc.add_GerenciadorNotasServicer_to_server(servidor.GerenciadorNotasServicer(), server)
    port = server.add_insecure_port('[::]:50053')
    server.start()
    yield f'localhost:{port}'
    server.stop(0)

@pytest.fixture(scope="module")
def stub(grpc_server):
    """Cria o cliente (Stub) para comunicar com o servidor de testes."""
    channel = grpc.insecure_channel(grpc_server)
    yield notas_pb2_grpc.GerenciadorNotasStub(channel)
    channel.close()

def test_cadastro_e_consulta_preservam_campos(stub):
    """Cadastro e consulta preservam todos os campos."""
    req = notas_pb2.AdicionaNotaRequest(ra="100", cod_disciplina="COMP01", ano=2026, semestre=1, nota=8.5)
    resp_add = stub.AdicionarNota(req)
    assert resp_add.sucesso is True
    
    resp_consulta = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="100", cod_disciplina="COMP01"))
    assert resp_consulta.sucesso is True
    assert resp_consulta.nota.ra == "100"
    assert resp_consulta.nota.cod_disciplina == "COMP01"
    assert resp_consulta.nota.ano == 2026
    assert resp_consulta.nota.semestre == 1
    assert resp_consulta.nota.nota == 8.5

def test_cadastro_duplicado_falha(stub):
    """Cadastro duplicado falha e mantém a nota original."""
    req = notas_pb2.AdicionaNotaRequest(ra="100", cod_disciplina="COMP01", ano=2026, semestre=1, nota=5.0)
    resp_add = stub.AdicionarNota(req)
    assert resp_add.sucesso is False # Já foi adicionada no teste anterior
    
    resp_consulta = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="100", cod_disciplina="COMP01"))
    assert resp_consulta.nota.nota == 8.5 # A nota original deve ser mantida

def test_consulta_nota_inexistente(stub):
    """Consulta de nota inexistente informa falha."""
    resp = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="100", cod_disciplina="COMP99"))
    assert resp.sucesso is False

def test_alteracao_atualiza_campos(stub):
    """Alteração atualiza nota, ano e semestre."""
    req = notas_pb2.AdicionaNotaRequest(ra="100", cod_disciplina="COMP01", ano=2027, semestre=2, nota=10.0)
    resp_alt = stub.AlterarNota(req)
    assert resp_alt.sucesso is True
    
    resp_consulta = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="100", cod_disciplina="COMP01"))
    assert resp_consulta.nota.nota == 10.0
    assert resp_consulta.nota.ano == 2027
    assert resp_consulta.nota.semestre == 2

def test_alterar_nota_inexistente(stub):
    """Alterar nota inexistente falha e não cria um cadastro."""
    req = notas_pb2.AdicionaNotaRequest(ra="101", cod_disciplina="COMP02", ano=2026, semestre=1, nota=7.0)
    resp_alt = stub.AlterarNota(req)
    assert resp_alt.sucesso is False
    
    resp_consulta = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="101", cod_disciplina="COMP02"))
    assert resp_consulta.sucesso is False

def test_media_ignora_outros_alunos(stub):
    """Média de 6 e 9 é 7,5; notas de outro aluno não entram."""
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="200", cod_disciplina="DISC1", ano=2026, semestre=1, nota=6.0))
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="200", cod_disciplina="DISC2", ano=2026, semestre=1, nota=9.0))
    
    # Adicionando nota para outro aluno
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="201", cod_disciplina="DISC1", ano=2026, semestre=1, nota=2.0))
    
    resp = stub.CalcularMedia(notas_pb2.AlunoRequest(ra="200"))
    assert resp.sucesso is True
    assert resp.media == 7.5

def test_media_aluno_sem_notas(stub):
    """Aluno sem notas recebe falha no cálculo da média."""
    resp = stub.CalcularMedia(notas_pb2.AlunoRequest(ra="999"))
    assert resp.sucesso is False

def test_media_usa_valor_atualizado(stub):
    """Média usa o valor atualizado da nota."""
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="300", cod_disciplina="DISC1", ano=2026, semestre=1, nota=5.0))
    stub.AlterarNota(notas_pb2.AdicionaNotaRequest(ra="300", cod_disciplina="DISC1", ano=2026, semestre=1, nota=10.0))
    
    resp = stub.CalcularMedia(notas_pb2.AlunoRequest(ra="300"))
    assert resp.sucesso is True
    assert resp.media == 10.0

def test_stream_entrega_somente_ra_solicitado(stub):
    """Stream entrega todas as notas e somente as do RA solicitado."""
    # Garante que o aluno 200 tem 2 notas e o 201 tem 1 nota (inseridas nos testes anteriores)
    stream = stub.ListarNotasAluno(notas_pb2.AlunoRequest(ra="200"))
    notas_recebidas = list(stream)
    
    assert len(notas_recebidas) == 2
    for nota in notas_recebidas:
        assert nota.ra == "200"

def test_stream_aluno_sem_notas(stub):
    """Aluno sem notas recebe um stream vazio."""
    stream = stub.ListarNotasAluno(notas_pb2.AlunoRequest(ra="888"))
    notas_recebidas = list(stream)
    assert len(notas_recebidas) == 0

def test_notas_extremas_media(stub):
    """Notas 0 e 10 são armazenadas e produzem média 5."""
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="400", cod_disciplina="DISC1", ano=2026, semestre=1, nota=0.0))
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="400", cod_disciplina="DISC2", ano=2026, semestre=1, nota=10.0))
    
    resp = stub.CalcularMedia(notas_pb2.AlunoRequest(ra="400"))
    assert resp.sucesso is True
    assert resp.media == 5.0

def test_disciplina_diferente_por_aluno(stub):
    """Uma disciplina pode ter notas diferentes para dois alunos."""
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="500", cod_disciplina="MAT01", ano=2026, semestre=1, nota=4.0))
    stub.AdicionarNota(notas_pb2.AdicionaNotaRequest(ra="501", cod_disciplina="MAT01", ano=2026, semestre=1, nota=8.0))
    
    resp_500 = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="500", cod_disciplina="MAT01"))
    resp_501 = stub.ConsultarNota(notas_pb2.AlunoDisciplinaRequest(ra="501", cod_disciplina="MAT01"))
    
    assert resp_500.nota.nota == 4.0
    assert resp_501.nota.nota == 8.0