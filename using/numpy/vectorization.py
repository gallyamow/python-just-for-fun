import numpy as np

def main():
    print(vectorization_way())
    print(loop_way())

def vectorization_way():
    arr = np.array([1, 2, 3, 4, 5])

    # Векторно
    squared = arr ** 2
    return squared

def loop_way():
    arr = np.array([1, 2, 3, 4, 5])
    squared = np.zeros(len(arr))

    # На цикле
    for i in range(len(arr)):
        squared[i] = arr[i] ** 2

    return squared


if __name__ == '__main__':
    main()