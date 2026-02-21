from multiprocessing import Pool
import os
from datetime import datetime
import time


def op(x):
    print(f'Process {os.getpid()} started at "{datetime.now()}"')

    time.sleep(0.2)
    v = x * x

    print(f'Process {os.getpid()} returns result {v} at "{datetime.now()}"')
    return v


"""
Для чего: 
Pool в Python из модуля multiprocessing нужен для удобного создания процессов и распределения задач между ними.

Как реализован:
счётчик + условная переменная (condition)

Метод map():
Каждое значение из списка передаётся функции.
Задачи выполняются параллельно, но results возвращаются в порядке переданного списка, блокируется пока все не будут готовы.

Метод starmap():
Для передачи нескольких аргументов.

Метод apply():
Выполняет одну функцию в одном процессе. Блокируется до результата.

Метод apply_async():
Выполняет одну функцию в одном процессе, результат будет позже. Возвращает ApplyResult (future-подобный).
"""


def using_pool():
    with Pool(4) as p:
        # waits all
        print("map")
        results = p.map(op, [1, 2, 3, 4, 5])
        print(results)

        # apply one operation
        print("apply")
        result = p.apply(op, (1,))
        print(result)

        # apply one operation
        print("apply_async")
        result = p.apply_async(op, (1,))
        print(result, result.get())


if __name__ == "__main__":
    using_pool()
