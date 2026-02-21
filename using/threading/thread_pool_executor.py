import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from random import random


# operation
def op(n: int) -> int:
    t = random()
    time.sleep(t)
    print(f"op({n}) = {n * n}, sleep = {t}")
    return n * n


if __name__ == "__main__":
    q = Queue()

    print("Way 1: using submit + blocking future.result")
    # Ждем каждый результат по порядку отправки задач, даже если другие задачи уже завершились раньше.
    # Часто это неэффективно, если первая задача долго выполняется, а другие уже готовы.
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(10):
            future = executor.submit(op, i)
            # future.result() блокирует поток, пока задача не завершится.
            print(future.result())
    print()

    print("Way 2: using executor.map")
    # Задачи запускаются параллельно (до max_workers одновременно).
    # Результаты возвращаются в том же порядке, что и переданные аргументы (0..9).
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(op, [i for i in range(10)])
    for res in results:
        print(res)
    print()

    print("Way 3: using executor.submit and as_completed")
    # Все задачи запускаются сразу.
    # as_completed(futures) возвращает итератор, который отдаёт Future по мере завершения задачи.
    # Вы не ждёте задачи по порядку отправки, а получаете результат, как только он готов.
    # Отлично подходит для задач с разной длительностью, чтобы выводить или обрабатывать результаты сразу, без ожидания самых медленных задач.
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(op, i) for i in range(10)]

        for future in as_completed(futures):
            print(future.result())
    print()
