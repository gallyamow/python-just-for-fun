"""
threading = лёгкий способ параллельно выполнять I/O операции.
Для CPU-bound задач многопоточность не ускоряет Python из-за GIL.
Всегда используйте Lock при работе с общими ресурсами.

Каждый поток выполняется одновременно, но в Python из-за GIL настоящий параллелизм по CPU ограничен.
Идеально подходит для I/O-bound задач (сеть, чтение/запись файлов).
Для CPU-bound задач лучше использовать multiprocessing.

## Основные объекты:

Thread	Основной объект для создания потока. Выполняет функцию параллельно с основным потоком.
Lock	Примитив блокировки для защиты критической секции.
RLock	Рекурсивная блокировка — один поток может захватывать несколько раз.
Event	Событие для синхронизации потоков (wait/set/clear).
Semaphore	Ограничивает количество потоков, одновременно выполняющих определённую часть кода.
Condition	Для сложной синхронизации потоков с ожиданием и уведомлением.
current_thread()	Возвращает объект текущего потока.
active_count()	Количество активных потоков.
enumerate()	Список всех активных потоков.

Потоки позволяют выполнять I/O-bound задачи параллельно.
Для CPU-bound задач лучше использовать multiprocessing, чтобы обойти GIL.
Lock, RLock, Semaphore, Event, Condition — инструменты для безопасной работы с общими ресурсами.
Thread.start() → запуск, Thread.join() → ожидание завершения.
"""
import os
import threading
import time


def worker(name):
    print(f"Worker {name}, PID: {os.getpid()}")
    time.sleep(0.5)

def simple():
    t1 = threading.Thread(target=worker, args=("Thread-1",))
    t2 = threading.Thread(target=worker, args=("Thread-2",))

    t1.start()
    t2.start()

    # ожидание завершения потока
    # (можно указать timeout, после таймаута процесс может всё ещё выполняться, но основной поток продолжит работу.)
    t1.join()
    t2.join()

    print("All threads finished")

def with_lock():
    counter = 0
    lock = threading.Lock()

    def increment():
        nonlocal counter

        for _ in range(1000):
            # Без lock значение counter может быть некорректным из-за состояния гонки.
            # with lock гарантирует, что только один поток одновременно изменяет переменную.
            with lock:
                counter += 1

    threads = [threading.Thread(target=increment) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("Counter:", counter)


if __name__ == '__main__':
    # Просто 2 потока
    print("SIMPLE")
    simple()
    print()

    # С lock для разделения общего ресурса
    print("WITH_LOCK")
    with_lock()
    print()
