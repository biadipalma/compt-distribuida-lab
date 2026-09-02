from mpi4py import MPI
# 1. Inicializa o ambiente de execução MPI (feito ao importar mpi4py)
comm = MPI.COMM_WORLD
# Lógica do programa paralelo aqui...
size = comm.Get_size()
rank = comm.Get_rank()
print("Processo", rank, "de", size)
# 2. Finaliza o ambiente MPI (opcional; ao sair, mpi4py finaliza)
# MPI.Finalize() # só se precisar encerrar explicitamente