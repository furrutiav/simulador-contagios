from time import sleep

N = 0
print('hola', end="\r")
for i in range(N):
    sleep(1)
    print(f"{i / N * 100:.1f} %", end="\r")

a = [[0, 1], [2, 3]]

print(a[0][1])