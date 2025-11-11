import threading
import time

"""
Для чего: 
Простое оповещение ждущих.
Поток может ждать события (`wait`) или оповещать другие потоки (`set`)  

Как реализован: Condition + bool flag.

Метод wait:
Захватывает Cond.Lock
Если флаг уже True - то сразу return.
Если нет, то wait не Cond.

Метод set:
Захватывает Cond.Lock
Cond.notify_all
"""
if __name__ == '__main__':
    event = threading.Event()

    def waiter():
        print("Waiting for event", flush=True)
        # Блокируется пока интервальный флаг не будет True
        event.wait()
        print("Event received!", flush=True)


    def setter():
        time.sleep(2)
        # Устанавливает интервальный флаг в True.
        # Действует на все потоки сразу.
        event.set()


    threading.Thread(target=waiter).start()
    threading.Thread(target=waiter).start()
    threading.Thread(target=waiter).start()
    threading.Thread(target=setter).start()
