import os
import random
import threading
import time

"""
Lock = Mutex

Для чего: 
Lock - Простейшая блокировка, позволяет только одному потоку работать с критической секцией
RLock - Рекурсивная блокировка — один и тот же поток может захватывать несколько раз.

Как реализован:

В CPython threading.Lock — это тонкая обёртка над примитивом блокировки операционной системы (Linux/macOS — pthread_mutex_t). 
Код написан на C.

Есть bool состояния замка locked и список waiters.

Метод acquire: 
1) Если не locked, тогда атомарно делаем его locked и выходим из функции.
2) Если locked, значит добавляем этот поток в список waiters и начинаем на этом потоке блокирующее ожидание (wait).
Если этот waiter попал в список пробужденных, он в какой то момент перестает отпускает метод wait и идет дальше.
Потом проверяем locked, если он False то меняем его на True и считается что мы захватили lock, возврашает true.
Иначе считается что не удалось захватить и возвращаем false.

Метод release: 
1) Проверка что locked = True иначе exception
2) Делаем locked =  False и пробуждаем какой то из waiters.

RLock построен на основе Lock и написан на Python.

Ниже объяснение человеческим языком + упрощённая псевдо-реализация.
"""


def non_reentrant_lock():
    """
    Обычный Lock нельзя захватить повторно из того же потока → будет deadlock.
    Потому что Lock хранит только два состояния: locked и unlocked.
    И он не знает, кто его заблокировал. Когда тот же поток пытается повторно войти — он получает
    “lock is already acquired” и блокируется сам на себя → deadlock.
    """
    locked_counter = 0
    non_locked_counter = 0
    lock = threading.Lock()

    def locked_increment():
        nonlocal locked_counter
        for _ in range(1000):
            with lock:
                locked_counter += 1

    def non_locked_increment():
        nonlocal non_locked_counter
        for _ in range(1000):
            non_locked_counter += 1

    threads = ([threading.Thread(target=locked_increment) for _ in range(10)]
               + [threading.Thread(target=non_locked_increment) for _ in range(10)])

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # не получилось добиться разности показателей
    print("locked_counter:", locked_counter)
    print("non_locked_counter:", non_locked_counter)


def reentrant_lock():
    """
    Реентерабельный (рекурсивный) Lock.
    RLock хранит ещё: 1) id потока, который владеет блокировкой 2) счётчик повторных захватов (_count)
    Когда реально использовать RLock:
     * когда у вас есть рекурсивные функции, которые используют один lock
     * когда метод класса вызывает другой метод, и оба используют один и тот же lock
     * когда вы оборачиваете критические секции декораторами, и lock может быть вложенным
    В golang специально нельзя получить инфу о goroutine, поэтому там и такого Lock нет.
    """
    lock = threading.RLock()

    def inner():
        print("inner: trying lock")
        with lock:  # повторный захват — OK
            print("inner: inside lock")

    def outer():
        print("outer: trying lock")
        with lock:  # первый захват
            print("outer: inside lock")
            inner()  # вызывает функцию, которая тоже берет lock

    thread = threading.Thread(target=outer)
    thread.start()
    thread.join()

def target_func(name):
    print(f"Target {name}, PID: {os.getpid()}", flush=True)
    t = random.random()
    time.sleep(t)


if __name__ == '__main__':
    non_reentrant_lock()
    print()
    reentrant_lock()
    print()
