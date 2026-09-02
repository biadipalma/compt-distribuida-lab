from mpi4py import MPI
import random
import time

comm = MPI.COMM_WORLD

rank = comm.Get_rank()
size = comm.Get_size()

N = 10000000

inicio = time.time()

dentro_local = 0

for _ in range(N):
    x = random.random()
    y = random.random()

    if x*x + y*y <= 1:
        dentro_local += 1

total_dentro = comm.reduce(
    dentro_local,
    op=MPI.SUM,
    root=0
)

fim = time.time()

if rank == 0:

    total_pontos = N * size

    pi = 4 * total_dentro / total_pontos

    tempo = (fim - inicio) * 1000

    print("================================")
    print("Estimativa de PI - MPI")
    print("================================")
    print("Processos:", size)
    print("Pontos por processo:", N)
    print("Total de pontos:", total_pontos)
    print("PI aproximado:", pi)
    print("Tempo:", tempo, "ms")
    print("================================")
