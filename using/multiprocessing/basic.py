"""
Модуль multiprocessing позволяет запускать процессы, каждый со своей памятью.
В отличие от потоков (threading), процессы не разделяют память, что обходит GIL (Global Interpreter Lock).
Полезно для CPU-bound задач (тяжёлые вычисления), когда многопоточность в Python не ускоряет.

## Основные объекты:

Process	создаёт отдельный процесс, аналог Thread
Queue	обмен данными между процессами
Pipe	канал для связи двух процессов
Pool	пул процессов для параллельного выполнения задач

## Отличие	multiprocessing	asyncio
Тип задач	CPU-bound	                        I/O-bound
Параллелизм	Настоящий (несколько процессов)	    Кооперативный (один поток, события)
Память	Каждый процесс отдельная память	        Общая память, но GIL ограничивает CPU
Сложность	Сложнее, нужен обмен данными	    Легче, управление через await
"""
import multiprocessing
import os
import time


def worker(name):
    print(f"Worker {name}, PID: {os.getpid()}")
    time.sleep(0.5)


def op(param):
    print(f"Operation {param}, PID: {os.getpid()}")
    time.sleep(0.5)


def producer(q):
    for i in range(5):
        q.put(i)
    q.put(None)  # сигнал конца


def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print("Consumed", item)


def simple():
    p1 = multiprocessing.Process(target=worker, args=("A",))
    p2 = multiprocessing.Process(target=worker, args=("B",))

    p1.start()
    p2.start()

    # ожидание завершения потока или процесса
    # (можно указать timeout, после таймаута процесс может всё ещё выполняться, но основной поток продолжит работу.)
    p1.join()
    p2.join()


def pool():
    with multiprocessing.Pool(2) as p:
        results = p.map(op, ["1", "2", "3", "4"])

    # Результаты возвращаются после выполнения всех задач.
    print("Results:", results)


def communication():
    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=producer, args=(q,))
    p2 = multiprocessing.Process(target=consumer, args=(q,))

    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == '__main__':
    # Просто 2 процесса
    print("SIMPLE")
    simple()
    print()

    # Пул процессов
    print("POOL")
    pool()
    print()

    # Коммуникация процессов
    print("COMMUNICATION")
    communication()
    print()
