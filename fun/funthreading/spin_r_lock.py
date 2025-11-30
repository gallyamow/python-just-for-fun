import threading
import time


class SpinRLock:
    """
    Аналог threading.RLock реализованный на цикле (spin).
    """

    def __init__(self):
        self.__locked = False
        self.__owner = None
        self.__lock_count = 0

    def acquire(self, blocking=True, timeout=-1) -> bool:
        start = time.time()

        while True:
            if not self.__locked:
                self.__locked = True
                self.__owner = threading.get_ident()
                self.__lock_count += 1
                return True

            if not blocking:
                return False

            # если поток тот же самый то, позволяем взять повторно
            if self.__locked and self.__owner == threading.get_ident():
                self.__lock_count += 1
                return True

            if timeout != -1 and (time.time() - start) >= timeout:
                return False

            time.sleep(0.01)

    def release(self):
        if not self.__locked:
            raise RuntimeError('Lock is not acquired')

        # Остался последний lock
        if self.__lock_count == 1:
            self.__locked = False
            self.__owner = None
            self.__lock_count = 0
            return

        # -1 lock
        self.__lock_count -= 1

    def locked(self) -> bool:
        return self.__locked

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
