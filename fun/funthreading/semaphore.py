import time

from .condition import Condition


class Semaphore:
    """
    Аналог threading.Semaphore.

    Для чего:
    - Semaphore - Он помогает ограничивать количество потоков, которые могут одновременно выполнять определённый участок кода.

    Как работает:
    Вариант 1: Счетчик + Lock
    Вариант 2: Счетчик + Condition
    2.1) Держим counter и Condition
    2.2) Если counter == 0 блокируемся на Condition с проверкой условия
    2.3) Если counter > 0 разрешаем занять слот.

    1) Метод acquire(blocking, timeout): Пытается захватить семафор если еще есть слоты. Обязательно true один из 2 флагов.
    2) Метод release(n=1): Освободить n-слотов семафора.
    3) Поддерживает with-context.
    """

    __slots__ = ('__counter', '__cond')

    def __init__(self, value=1):
        # 0 - быть разрешено
        if value < 0:
            raise ValueError('n must be zero or more')

        self.__counter = value
        self.__cond = Condition()

    def acquire(self, blocking=True, timeout=None) -> bool:
        if not blocking and timeout is not None:
            raise ValueError("can't specify timeout for non-blocking acquire")

        with self.__cond:
            start_waiting = time.time()
            while self.__counter == 0:
                # Цикл прокрутили и 1 раз проверили, в неблокирующем режиме уже можно вернуть False
                if not blocking:
                    return False

                # Если таймаут задан, то не можем уйти в wait.
                if timeout is not None:
                    # Не получилось захватить семафор, время вышло.
                    if time.time() - start_waiting > timeout:
                        return False
                    continue

                # Если таймаута нет, то можем блокироваться
                self.__cond.wait()

            # Удалось захватить семафор
            self.__counter -= 1

            return True

    def release(self, n=1):
        if n < 1:
            raise ValueError('n must be one or more')

        with self.__cond:
            self.__counter += n
            self.__cond.notify(n)

    # @idiomatic: method aliasing
    __enter__ = acquire

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
