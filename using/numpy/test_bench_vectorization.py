import numpy as np


def test_bench_loop(benchmark):
    benchmark(loop)


def test_bench_vector(benchmark):
    benchmark(vector)


def vector():
    arr = np.arange(1, 1000)
    return arr**2


def loop():
    arr = np.arange(1, 1000)
    for i in range(len(arr)):
        arr[i] = arr[i] ** 2
    return arr
