import threading
import time

from .condition import Condition as FunCondition
from threading import Condition as NativeCondition


def te2st_counter_of_fun():
    condition = FunCondition()
    counter(condition)


def test_counter_of_native():
    condition = NativeCondition()
    counter(condition)


def counter(condition):
    # @idiomatic: using counter instead of bool
    # (bool использовать не получится, так как consumer может например 2 раза захватить lock:
    # - Если producer вызвал notify() до того, как consumer вошёл в wait(), consumer может пропустить событие.
    #   Булев флаг уже True, но consumer может проверить его позже и не заметить изменения.
    # - Булевый флаг может хранить только два состояния: True/False, поэтому если producer быстро делает несколько
    #   notify подряд, consumer обработает только один сигнал.
    events = 0
    res= 0
    ready: bool = False

    def producer():
        nonlocal ready, events

        for _ in range(10):
            # @idiomatic: correct way to sleep
            # (лучше вызывать вне lock, чтобы не блокировать другие потоки)
            time.sleep(0.1)

            # @idiomatic: correct way to notify signal
            # (должен охватывать только критическую секцию, а не весь цикл sleep)
            with condition:
                ready = True
                events += 1
                condition.notify()

        # оповещаем, чтобы если есть последний consumer он вышел из wait
        with condition:
            condition.notify_all()

    def consumer():
        nonlocal res, ready

        while events < 10:
            with condition:
                # @idiomatic: correct way to wait signal
                # (иначе если producer вызвал notify до того, как consumer вошёл в wait(), сигнал потеряется.)
                while not ready:
                    condition.wait()

                res += 1
                ready = False

    t1 = threading.Thread(target=producer)
    t2 = threading.Thread(target=consumer)

    t1.start()
    time.sleep(0.2)

    t2.start()

    t1.join()
    t2.join()

    assert res == 10
