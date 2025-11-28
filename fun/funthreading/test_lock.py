import threading
import time

from .spinlock import SpinLock as FunLock
from threading import Lock as NativeLock


def test_counter_fun_lock():
    lock = FunLock()
    counter_with(lock)


def test_counter_native_lock():
    lock = NativeLock()
    counter_with(lock)


def counter_with(lock):
    cnt = 0

    def worker():
        nonlocal cnt
        for _ in range(100):
            with lock:
                temp = cnt
                time.sleep(0.0001)
                cnt = temp + 1

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert cnt == 100 * 10, f"got {cnt} want {100 * 10}"
