import threading
import time


class SpinRLock:
    """
    Аналог threading.RLock, реализованный через активное ожидание (spinlock).
    Поддерживает повторный захват блокировки одним и тем же потоком.

    Дополнительно можно реализовать справедливый (fair) lock: его особенность в том что второй раз lock захватит тот
    кто дольше всех ждет, чтобы не было "голодания" (starvation).
    Для этого надо хранить waiters в массиве и отдавать lock первому из списка (убрав его из head).
    """

    # @idiomatic: используем slots для оптимизации памяти
    # Свойства храним в slots:
    #  - потому что свойства добавлять динамически мы не собираемся
    #  - доступ немного быстрее
    #  - не добавим случайно новое свойство
    # Минусы:
    #  - усложняется наследование
    #  - Нет __dict__, значит некоторые возможности рефлексии, сериализации, динамических патчей сложнее.
    #  - Например, pickle/JSON и некоторые фреймворки ожидают наличие __dict__.
    #  - Некоторые инструменты разработки (например, Django ORM) активно используют __dict__
    __slots__ = ("__locked", "__owner", "__lock_count")

    def __init__(self):
        # @idiomatic: typing
        self.__locked: bool = False
        self.__owner: int | None = None
        self.__lock_count: int = 0

    def acquire(self, blocking=True, timeout=-1) -> bool:
        thread_id = threading.get_ident()
        start = time.time()

        while True:
            if not self.__locked:
                self.__locked = True
                self.__owner = thread_id
                self.__lock_count = 1
                return True

            if not blocking:
                return False

            # если поток тот же самый то, позволяем взять повторно
            if self.__owner == thread_id:
                self.__lock_count += 1
                return True

            if timeout != -1 and (time.time() - start) >= timeout:
                return False

            time.sleep(0.001)

    def release(self):
        thread_id = threading.get_ident()

        if not self.__locked:
            raise RuntimeError("SpinRLock is not acquired")

        if self.__owner != thread_id:
            raise RuntimeError("SpinRLock: lock can be released only by the owner")

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

    # Безусловно освобождает блокировку возвращая состояние.
    # (специальный protected метод для использования в Condition)
    def _release_save(self) -> tuple[int, int]:
        cnt = self.__lock_count
        if cnt == 0:
            raise RuntimeError("cannot release un-acquired lock")
        owner = self.__owner

        self.__locked = False
        self.__owner = None
        self.__lock_count = 0

        return cnt, owner

    # Захватывает блокировку устанавливая переданное состояние.
    # (специальный protected метод для использования в Condition)
    def _acquire_restore(self, state: tuple[int, int]):
        cnt, owner = state
        self.acquire()
        self.__lock_count = cnt
        self.__owner = owner
