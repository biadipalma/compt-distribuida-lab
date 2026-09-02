import random
import time

N = 300
A = [[random.random() for _ in range(N)] for _ in range(N)]
B = [[random.random() for _ in range(N)] for _ in range(N)]
C = [[0] * N for _ in range(N)]

inicio = time.time()

for i in range(N):
    for j in range(N):
        for k in range(N):
            C[i][j] += A[i][k] * B[k][j]

fim = time.time()

print("Tempo sequencial:", (fim - inicio) * 1000, "ms")