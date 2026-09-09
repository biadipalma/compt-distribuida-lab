from mpi4py import MPI
import random

# Inicialização do MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# =============================
# Função para gerar logs
# =============================
def gerar_logs(qtd):

    ips = [f"192.168.1.{i}" for i in range(1, 255)]

    endpoints = [
        "/",
        "/login",
        "/products",
        "/cart",
        "/checkout",
        "/api/users",
        "/api/orders"
    ]

    metodos = ["GET", "POST"]
    status = ["200", "200", "200", "404", "500"]
    logs = []
#gerar dados do log

    for i in range(qtd):
        #random choice ele escolhe aleatoriamente dos logs numa lista
        ip = random.choice(ips) #192.168.1. ...
        metodo = random.choice(metodos) #GET ou POST
        endpoint = random.choice(endpoints) #login
        codigo = random.choice(status) #200,404,500

        linha = f"{ip} {metodo} {endpoint} {codigo}" #junta tudo

        logs.append(linha) #add elemente no final da lista

    return logs


# =============================
# Processo 0 gera o dataset
# =============================

logs_divididos = None
TOTAL_LOGS = 1000000

if rank == 0:

    print("\n==============================")
    print("Gerando dataset de logs...")
    print("==============================\n")
    logs = gerar_logs(TOTAL_LOGS)

    # qnt de logs para cada processo
    quantidade_por_processo = TOTAL_LOGS // size

    # guarda as partes dos logs.
    logs_divididos = []

    for i in range(size):

        inicio = i * quantidade_por_processo

        fim = inicio + quantidade_por_processo

        parte = logs[inicio:fim] #divide a lista 

        logs_divididos.append(parte)


# =============================
# Distribuição usando Scatter
# =============================

logs_locais = comm.scatter( #recebe somente uma parte.
    logs_divididos,
    root=0 #responsável por enviar os dados é o processo 0.
)


# =============================
# Processamento local
# =============================

erros = 0 #conta a qnt de erros q encontrou 

for linha in logs_locais: #p/ cada linha vai fazer uma analise

    campos = linha.split() 

    status = campos[3] #faz ele começar pelo parte dos status

    if status == "404" or status == "500":

        erros += 1


# =============================
# Resultado local
# =============================

print(
    f"Processo {rank} analisou "
    f"{len(logs_locais)} linhas "
    f"e encontrou {erros} erros."
)
