"""
Упрощенная реализация coroutine (на основе генератора) и упрощенный event-loop для выполнения ее await.
"""

from time import sleep
from typing import Callable, Any


class Call:
    """
    Отложенный синхронный вызов.

    Аналог:
    await loop.run_in_executor(...)
    """

    def __init__(self, func: Callable[..., Any], *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.func(*self.args, **self.kwargs)

    def __repr__(self):
        return f"Call({self.func.__name__}, args={self.args})"


def run(gen):
    """
    run() — упрощённый аналог asyncio.run()
    """
    try:
        # 1) Стартует: получает Call через yield
        # (coroutine priming)
        call = next(gen)
        print("received call:", call)

        # 2) Прокручивает генератор до конца
        while True:
            # 3) Выполняет Call синхронно
            # (аналог await)
            val = call()
            print("awaited result:", val)

            # 4) Отправляет результат обратно через send()
            # 5) ВАЖНО: И берем новый call
            # (продолжаем coroutine)
            call = gen.send(val)
            print("received call:", call)
    except StopIteration as e:
        # Возвращает финальный результат через StopIteration.value
        return e.value


# имитация блокирующей операции
def sync_square(x: int) -> int:
    """
    Синхронная функция.
    """
    sleep(1)
    return x * x


def async_sum_of_squares(x: int, y: int):
    """
    Асинхронная функция.
    (generator-based coroutine)

    yield Call(...)  ≈  await something
    send(result)     ≈  возобновление coroutine
    return           ≈  результат asyncio.run()
    """
    part1 = yield Call(sync_square, x)
    part2 = yield Call(sync_square, y)

    return part1 + part2


if __name__ == "__main__":
    result = run(async_sum_of_squares(2, 3))
    print(f"result = {result}")
