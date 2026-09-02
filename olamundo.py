from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank != 0:
    mensagem = f"Saudações do processo {rank} de {size}"
    comm.send(mensagem, dest=0)
else:
    print(f"Saudações do processo {rank} de {size}")
    for i in range(1, size):
        mensagem = comm.recv(source=i)
        print(mensagem)