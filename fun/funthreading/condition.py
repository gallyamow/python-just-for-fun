import threading
from typing import List

from .spin_r_lock import SpinRLock
from .spin_lock import SpinLock


class Condition:
    """
    Для чего:
    Позволяет ожидать изменений, так чтобы не расходовать CPU на активное ожидание.
    Принцип работы с ним: проверяем условие, если оно еще нам не подходим, то вызываем wait() и начинаем ждать без расхода CPU.
    Условие должно проверяться в цикле, методы вызываться с захваченной блокировкой RLock.

    Как работает:
    1) Главная блокировка RLock и набора Lock для каждого ждущего потока.
    2) Метод wait: предназначен, чтобы встать в очередь на ожидание изменения условия.
       2.1) Чтобы waiter начал ждать, он должен вызывать wait. При этом он сначала ждет захвата главной блокировки, и только после этого вызывает wait.
       2.2) Метод wait создает для вызывающего свою персональную блокировку Lock, сразу ее захватывает, помещает ее в список блокировок.
       2.3) Освобождаем основной lock, чтобы другие тоже могли поработать (с особенностями по кол-ву)
       2.4) Далее, вызывающий сам же пытается захватить свой персональный Lock() во второй раз, и таким образом начинает ждать.
       2.5) Когда ему это удается, значит был notify. Значит поток может удалить себя из ожидающих (предварительно захватив RLock).
    3) Метод notify (notifyAll): предназначены, чтобы сообщить ожидающим, что условие поменялось и им надо начать работать.
    """
    __slots__ = ('__lock', '__waiters', '__locks_count')

    def __init__(self):
        self.__lock = SpinRLock()
        self.__waiters: List[SpinLock] = []
        self.__locks_count = 0

    # (метод должен вызываться с уже захваченным RLock)
    def wait(self, timeout=None) -> bool:
        # Захватываем главный reentrant lock
        self.__lock.acquire(timeout=-1 if timeout is None else timeout)

        # Для каждого ожидающего создаем обычный lock
        waiter = SpinLock()
        # Сразу его захватывает
        waiter.acquire()
        self.__waiters.append(waiter)

        # Отпускаем главный lock (особенным образом), это нужно чтобы остальные могли поработать и сделать notify.
        # Нюанс: если RLock захватывали несколько раз, то он должен отпускаться столько раз, сколько был захвачен.
        # А нам тут надо безусловно освободить, но потом вернуть как было.
        # Для этого используются специальные методы _release_save и _acquire_restore которые есть в RLock.
        # noinspection PyProtectedMember
        lock_state = self.__lock._release_save()

        try:
            # Waiter пытается захватить свой lock во второй раз и остается на нем висеть
            acquired = waiter.acquire(timeout=-1 if timeout is None else timeout)
        finally:
            # Здесь уже ожидающий дождался, значит убирает себя из списка ожидающих
            # Перед модификацией _waiters он должен захватить заново глобальный lock.
            # noinspection PyProtectedMember
            self.__lock._acquire_restore(lock_state)
            with self.__lock:
                if waiter in self.__waiters:
                    self.__waiters.remove(waiter)

        return acquired

    # (метод должен вызываться с уже захваченным RLock)
    def notify(self, n=1):
        with self.__lock:
            for _ in range(min(n, len(self.__waiters))):
                waiter = self.__waiters.pop(0)
                waiter.release()

    def notify_all(self):
        self.notify(len(self.__waiters))



    def __enter__(self):
        self.__lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__lock.release()
