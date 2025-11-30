import threading
import time
from threading import RLock as NativeLock
from .spin_r_lock import SpinRLock as FunLock


def test_counter_of_fun():
    lock = FunLock()
    counter_with(lock)


def test_counter_of_native():
    lock = NativeLock()
    counter_with(lock)


def test_timeout_of_fun():
    lock = FunLock()
    timeout(lock)


def test_timeout_of_native():
    lock = NativeLock()
    timeout(lock)


def test_non_blocking_of_fun():
    lock = FunLock()
    non_blocking(lock)


def test_non_blocking_of_native():
    lock = NativeLock()
    non_blocking(lock)


def test_reentrant_of_fun():
    lock = FunLock()
    reentrant(lock)


def test_reentrant_of_native():
    lock = NativeLock()
    reentrant(lock)


def counter_with(lock):
    cnt = 0

    def worker():
        nonlocal cnt
        for _ in range(100):
            # @idiomatic: with usage
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


def timeout(lock):
    last = time.time()

    def greedy_worker():
        with lock:
            time.sleep(0.5)

    def worker():
        nonlocal last

        # @idiomatic: manually usage to use some special options
        acquired = lock.acquire(timeout=0.2)
        now = time.time()
        since = now - last
        last = now
        assert acquired == False
        assert 0.19 < since < 0.25

        acquired = lock.acquire(timeout=0.2)
        now = time.time()
        since = now - last
        last = now
        assert acquired == False
        assert 0.19 < since < 0.25

        time.sleep(0.2)

        # greedy_worker lock should've been released, so it's time to acquire
        acquired = lock.acquire(timeout=0.2)
        assert acquired == True

    t1 = threading.Thread(target=greedy_worker)
    t2 = threading.Thread(target=worker)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


def non_blocking(lock):
    last = time.time()

    def greedy_worker():
        with lock:
            time.sleep(0.5)

    def worker():
        nonlocal last

        acquired = lock.acquire(blocking=False)
        now = time.time()
        since = now - last
        last = now
        assert acquired == False
        assert 0.0 < since < 0.02

        acquired = lock.acquire(blocking=False)
        now = time.time()
        since = now - last
        last = now
        assert acquired == False
        assert 0.0 < since < 0.02

    t1 = threading.Thread(target=greedy_worker)
    t2 = threading.Thread(target=worker)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


def reentrant(lock):
    # @idiomatic: manually usage to use some special options
    # просто first_locked = 0.0 было бы проще
    first_locked: float | None = None

    def greedy_worker():
        nonlocal first_locked

        with lock:
            assert lock.acquire()
            first_locked = time.time()

            assert lock.acquire()
            since = time.time() - first_locked
            assert 0.0 < since < 0.02  # instantly

            time.sleep(0.5)
            lock.release()

            time.sleep(0.5)
            lock.release()

    def worker():
        nonlocal first_locked

        while lock.acquire():
            since = time.time() - first_locked
            assert 1 < since < 1.2
            return

    t1 = threading.Thread(target=greedy_worker)
    t2 = threading.Thread(target=worker)

    t1.start()
    time.sleep(0.5)

    t2.start()

    t1.join()
    t2.join()
