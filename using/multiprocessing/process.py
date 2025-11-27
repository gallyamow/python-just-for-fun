"""
Process — это объект, который представляет отдельный процесс в операционной системе.
Каждый процесс имеет собственный интерпретатор Python и отдельную память.

Если указать p.daemon = True, то процесс завершится вместе с главным процессом
"""
import os
import time
from datetime import datetime
from multiprocessing import Process


def f(n):
    print(f'Process {os.getpid()} started at "{datetime.now()}"', flush=True)
    time.sleep(0.2)
    print(f'Process {os.getpid()} finished at "{datetime.now()}"', flush=True)


if __name__ == "__main__":
    processes = []

    for i in range(5):
        p = Process(target=f, args=(i,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
