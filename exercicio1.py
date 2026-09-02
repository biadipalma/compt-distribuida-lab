from mpi4py import MPI
import random
import time

comm = MPI.COMM_WORLD

rank = comm.Get_rank()
size = comm.Get_size()

N = 1000

if rank == 0:
    A = [[random.random() for _ in range(N)] for _ in range(N)]
    B = [[random.random() for _ in range(N)] for _ in range(N)]
else:
    A = None
    B = None

inicio = time.time()

A = comm.bcast(A, root=0)
B = comm.bcast(B, root=0)

linhas_por_processo = N // size

inicio_linha = rank * linhas_por_processo

if rank == size - 1:
    fim_linha = N
else:
    fim_linha = inicio_linha + linhas_por_processo

C_local = []

for i in range(inicio_linha, fim_linha):
    linha = []

    for j in range(N):
        soma = 0

        for k in range(N):
            soma += A[i][k] * B[k][j]

        linha.append(soma)

    C_local.append(linha)

resultado = comm.gather(C_local, root=0)

fim = time.time()

if rank == 0:
    C = []

    for parte in resultado:
        C.extend(parte)

    tempo = (fim - inicio) * 1000

    print("================================")
    print("Multiplicação de Matrizes - MPI")
    print("================================")
    print("Processos:", size)
    print("Tamanho da matriz:", N)
    print("Tempo:", tempo, "ms")
    print("Matriz final:", len(C), "x", len(C[0]))
    print("================================")
