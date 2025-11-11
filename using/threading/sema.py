import threading

"""
Для чего: 
Ограничивает количество потоков, выполняющих участок кода одновременно 

Как реализован:
счётчик + условная переменная (condition)

Метод acquire():
Захватив cond в цикле если слотов == 0 , переходим в cond.wait(). Если пробуждаемся, то новая итерация цикла и 
спячка если слотов снова нет.
Если же слоты есть, то выходим из цикла и уменьшаем слоты на 1.

Метод release()
_value += 1 — освободили место
notify() — разбудим один поток, который ждал acquire()
(Именно один, потому что слотов добавился только один.)
"""

def using_semaphore_with():
    sem = threading.Semaphore(3)

    counter = 0
    def handler():
        nonlocal counter

        with sem:
            print(f'sem acquired by {threading.current_thread().name}')
            counter += 1

        print(f'sem released by {threading.current_thread().name}, counter={counter}')

    threads = [threading.Thread(target=handler) for i in range(50)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

def using_semaphore_manually():
    sem = threading.Semaphore(3)

    counter = 0
    def handler():
        nonlocal counter

        sem.acquire()
        print(f'sem acquired by {threading.current_thread().name}')
        counter += 1
        sem.release()

        print(f'sem released by {threading.current_thread().name}, counter={counter}')

    threads = [threading.Thread(target=handler) for i in range(50)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    print("using_semaphore_with")
    using_semaphore_with()
    print()
