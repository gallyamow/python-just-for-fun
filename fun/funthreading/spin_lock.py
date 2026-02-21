import time


class SpinLock:
    """
    Аналог threading.Lock, реализованный через активное ожидание (spinlock).
    """

    __slots__ = "__locked"

    def __init__(self):
        self.__locked: bool = False

    def acquire(self, blocking=True, timeout=-1) -> bool:
        start = time.time()

        # Проверку делаем в цикле, если захватим то будет ровно одна итерация
        while True:
            # Удалось захватить блокировку
            if not self.__locked:
                self.__locked = True
                return True

            # Если активирован неблокирующий режим, то мы не должны уходить в цикл ожидания, поэтому возвращаем
            # флаг о том что не захватили
            if not blocking:
                return False

            # Если активирован таймаут, то можем ждать только до его истечения. Поэтому каждую итерацию проверяем это.
            # Можно наверно ускорить, если просто суммировать delays.
            if timeout != -1 and (time.time() - start) >= timeout:
                return False

            time.sleep(0.001)

    def release(self):
        if not self.__locked:
            raise RuntimeError("Lock is not acquired")
        self.__locked = False

    def locked(self) -> bool:
        return self.__locked

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
