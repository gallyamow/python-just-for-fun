import numpy as np


def creation():
    # матрица из нулей
    zeros = np.zeros((3, 3))
    print("zeros")
    print(zeros)
    print("shape", zeros.shape)
    print()

    # матрица из единиц
    ones = np.ones((2, 4))
    print("ones")
    print(ones)
    print("shape", ones.shape)
    print()

    # единичная матрица (диагональ единицы, остальное нули)
    eye = np.eye(3)
    print("eye")
    print(eye)
    print("shape", eye.shape)
    print()

    # массив содержащий элементы с приращением: 0 2 4 6 8
    interval = np.arange(0, 10, 2)
    print("interval")
    print(interval)
    print("interval", interval.shape)
    print()

    # 5 точек от 0 до 1, равномерно разделенных
    lspace = np.linspace(0, 1, 5)
    print("lspace")
    print(lspace)
    print("lspace", lspace.shape)
    print()

    # можно указать тип
    flo = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ], dtype=float)
    print("flo")
    print(flo)
    print()


def operations():
    # Перегрузка операторов позволяет записать операции очень ясно.

    a = np.array([1, 2, 3])
    print('a', a)
    print('a+10', a + 10)

    b = np.array([4, 5, 6])
    print('b', b)
    print('a+b', a + b)


def slices():
    a = np.array([10, 20, 30, 40])
    print('a[1:3]', a[1:3])

    m = np.array([[1, 2, 3], [4, 5, 6]])
    # значение 6
    print('m[1, 2]', m[1, 2])
    # 2-й столбец -> [2, 5]
    print('m[:, 1]', m[:, 1])
    # # 1-я строка -> [1, 2, 3]
    print('m[0]', m[0])


def filtering():
    a = np.array([1, 2, 3, 4, 5])
    print('a[a > 2]', a[a > 2])


def matrix():
    a = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20]])
    print("a")
    print(a)
    print()

    eye = np.eye(5)

    # умножение матриц (умножение на единичную - не меняет)
    print('a @ e')
    print(a @ eye)
    print()

    eye = eye * 2
    print('a @ e*2')
    print(a @ eye)
    print()


def linalg():
    # сингулярная (квадратная + определитель == 0)
    a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print('a')
    print(a)
    print()

    # определитель = 0
    # (характеризует ориентированное «растяжение» или «сжатие» многомерного евклидова пространства после
    # преобразования матрицей)
    d = np.linalg.det(a)
    print('det(a)', d)

    # псевдообратную можно считать и для сингулярной
    pinv = np.linalg.pinv(a)
    print('pinv')
    print(pinv)

    # обратную матрицу нельзя считать для сингулярной, поэтому немного "пошумим" ее (регуляризация)
    a_reg = a + 1e-8 * np.eye(a.shape[0])
    print('a_reg')
    print(a_reg)

    b = np.array([[1, 2, 3], [8, 9, 10], [2, 5, 7]])
    print('b')
    print(b)
    inv = np.linalg.inv(b)
    print('inv')
    print(inv)

    # проверим свойство обратной
    print('inv @ b')
    print(inv @ b)
    print()

    print("matrix_rank", np.linalg.matrix_rank(b))


def math():
    a = np.array([1, 2, 3, 4, 5])
    print("mean", np.mean(a))
    print("sum", np.sum(a))
    print("min", np.min(a))
    print("max", np.max(a))
    print("std", np.std(a))


def linear_equations_solve():
    a = np.array([[1, 2], [3, 4]])
    b = np.array([5, 6])
    x = np.linalg.solve(a, b)
    print(a, b, x)


if __name__ == '__main__':
    print('>>> creation')
    creation()
    print()

    print('>>> operations')
    operations()
    print()

    print('>>> slices')
    slices()
    print()

    print('>>> filtering')
    filtering()
    print()

    print('>>> math')
    math()
    print()

    print('>>> matrix')
    matrix()
    print()

    print('>>> linalg')
    linalg()
    print()

    print('>>> linear_equations_solve')
    linear_equations_solve()
    print()
