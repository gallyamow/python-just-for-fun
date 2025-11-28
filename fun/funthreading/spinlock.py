import time


class SpinLock:
    def __init__(self):
        self.__locked = False

    def acquire(self, blocking=True, timeout=-1):
        start = time.time()
        while True:
            # удалось захватить блокировку
            if not self.__locked:
                self.__locked = True
                return True

            # блокировка уже захвачена, в неблокирующем режиме вернуть False
            if not blocking:
                return False

            # крутим цикл до тех пор, пока блокировка не освободится кем то другим или пока не будет превышен таймаут
            # если он есть
            if timeout != -1 and (time.time() - start) >= timeout:
                return False

            time.sleep(0.01)

        return False

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
