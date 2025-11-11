import threading
from abc import ABC, abstractmethod
import queue


# @idiomatic: abstract class
class Task(ABC):
    # @idiomatic: callable class
    @abstractmethod
    def __call__(self):
        pass


class FibTask(Task):
    def __init__(self, n: int):
        self.n = n

    def __call__(self):
        return fib(self.n)


# Бесконечный цикл + очередь.
def worker(q: queue.Queue, worker_id: int):
    print(f"[Worker {worker_id}] started.")

    # Ждем постоянно sentinel
    while True:
        # по дефолту - блокируется если нет задач, есть возможность указать timeout
        task = q.get()

        # sentinel -> graceful shutdown
        # producer специально публикует None для завершения
        if task is None:
            print(f"[Worker {worker_id}] received signal top stop.", flush=True)
            # отмечаем что полученный task выполнен
            q.task_done()
            break

        # computing
        result = task()

        # Из-за буферизации вывода + многопоточная среда строки могут "слипаться", решение:
        # 1) принудительный flush 2) lock 3) logging
        print(f"[Worker {worker_id}] computing finished = {result}.", flush=True)
        q.task_done()


def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


# Альтернативные варианты построения queue + worker:
# 1) библиотека celery и хранение в брокере, возможность работы на разных серверах
# 2) asyncio
if __name__ == '__main__':
    task_queue = queue.Queue()

    workers = []
    for i in range(3):
        # Можно указать daemon=True - тогда он работает «в фоне», python не будет ждать, пока он завершится;
        # при завершении программы такие потоки принудительно уничтожаются.
        #
        # Daemon-потоки используют когда:
        # не хранит важные данные,
        # делает фоновые задачи, которые можно безопасно прервать,
        # не должен блокировать завершение программы.
        w = threading.Thread(target=worker, args=(task_queue, i))
        workers.append(w)
        w.start()

    # publish tasks
    for i in range(10):
        task_queue.put(FibTask(i))

    # @idiomatic: sentinel (сигнальное значение) pattern
    for _ in workers:
        # send sentinel values (one per worker)
        task_queue.put(None)

    # waiting result (не нужно join отдельных workers)
    task_queue.join()
