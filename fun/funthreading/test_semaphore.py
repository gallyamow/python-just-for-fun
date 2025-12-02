import threading
import time

import pytest

from .semaphore import Semaphore


def test_initial_value():
    sem = Semaphore(2)
    assert sem._Semaphore__counter == 2


def test_init_invalid_value():
    """Тест инициализации с некорректным значением"""
    # @idiomatic: wait exception
    with pytest.raises(ValueError, match="n must be zero or more"):
        Semaphore(-1)


def test_acquire_release_basic():
    sem = Semaphore(2)

    # first
    assert sem.acquire()
    assert sem._Semaphore__counter == 1

    # second
    assert sem.acquire()
    assert sem._Semaphore__counter == 0

    # first release
    sem.release()
    assert sem._Semaphore__counter == 1

    # second release
    sem.release()
    assert sem._Semaphore__counter == 2


def test_release_n():
    sem = Semaphore(3)
    assert sem.acquire()
    assert sem.acquire()
    assert sem.acquire()
    sem._Semaphore__counter == 0

    sem.release(4)
    assert sem._Semaphore__counter == 4


def test_release_invalid_value():
    """Тест освобождения с некорректным значением"""
    sem = Semaphore(1)

    with pytest.raises(ValueError, match="n must be one or more"):
        sem.release(0)

    with pytest.raises(ValueError, match="n must be one or more"):
        sem.release(-1)


def test_non_blocking_acquire():
    sem = Semaphore(0)
    assert not sem.acquire(blocking=False)


def test_timeout_acquire():
    sem = Semaphore(0)
    start = time.time()
    sem.acquire(True, 0.2)
    assert 0.2 < time.time() - start < 0.3


def test_invalid_acquire_parameters():
    """Тест невалидных параметров acquire"""
    sem = Semaphore(1)

    with pytest.raises(ValueError, match="can't specify timeout for non-blocking acquire"):
        sem.acquire(blocking=False, timeout=1)


def test_context_manager():
    sem = Semaphore(1)

    with sem:
        assert sem._Semaphore__counter == 0

    assert sem._Semaphore__counter == 1


def test_thread_wake_up():
    sem = Semaphore(0)
    res = []

    def worker():
        sem.acquire()
        res.append('acquired')

    t = threading.Thread(target=worker)
    t.start()

    time.sleep(0.1)
    sem.release()
    t.join()

    assert res == ['acquired']

def test_thread_wake_up_n():
    sem = Semaphore(3)
    res = []

    def worker(worker_id: int):
        sem.acquire()
        res.append(f'worker-{worker_id} acquired')

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()

    time.sleep(0.1)
    sem.release(3)

    for t in threads:
        t.join()

    assert res == [f'worker-{i} acquired' for i in range(3)]
