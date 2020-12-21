from numba import vectorize, jit, cuda, float64, guvectorize, int64, int32
import numpy as np
# to measure exec time
from timeit import default_timer as timer

# normal function to run on cpu
def func(a):
    for i in range(10000000):
        a[i]+= 1

@jit([(int64[:], int32, int64[:])])
def g(x, y, res):
    for i in range(x.shape[0]):
        res[i] = x[i] + y

if __name__=="__main__":
    n = 10000000
    start = timer()
    a = np.ones(n, dtype = np.int64)
    b = a.copy()
    print(timer() - start)

    start = timer()
    # func(a)
    print("without GPU:", timer()-start)

    start = timer()
    g(a, 6, a)
    print("with GPU:", timer()-start)
    print(a)
