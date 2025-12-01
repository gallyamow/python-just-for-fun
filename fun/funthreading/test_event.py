import threading
import time
from .event import Event


def test_initial_state():
    ev = Event()
    assert not ev.is_set()


def test_set_changes_flag():
    ev = Event()
    ev.set()
    assert ev.is_set()


def test_wait_returns_immediately_if_set():
    ev = Event()
    ev.set()

    t0 = time.time()
    ev.wait()
    dt = time.time() - t0

    assert dt < 0.01  # не должен блокировать


def test_wait_blocks_until_set():
    ev = Event()
    res = []

    def worker():
        ev.wait()
        res.append("done")

    t = threading.Thread(target=worker)
    t.start()

    time.sleep(0.05)
    assert res == []  # поток ещё ждёт

    ev.set()
    t.join(timeout=1)
    assert res == ["done"]


def test_clear_makes_wait_block_again():
    ev = Event()
    ev.set()
    assert ev.is_set()

    ev.clear()
    assert not ev.is_set()

    res = []

    def worker():
        ev.wait()
        res.append("done")

    t = threading.Thread(target=worker)
    t.start()

    time.sleep(0.05)
    assert res == []  # всё ещё ждёт

    ev.set()
    t.join(timeout=1)
    assert res == ["done"]


def test_wait_timeout():
    ev = Event()

    t0 = time.time()
    r = ev.wait(timeout=0.1)
    dt = time.time() - t0

    assert r is True
    assert dt >= 0.1
    assert not ev.is_set()
