import threading
import time


class Condition:
    def wait(self, timeout=None):
        pass

    def notify(self, n=1):
        pass

    def notify_all(self):
        pass


if __name__ == '__main__':
    cond = threading.Condition()
    response = None


    def producer():
        global response

        with cond:
            time.sleep(1)
            response = 'Secret response'
            cond.notify()
            print('Producer condition notified', flush=True)


    def consumer():
        print('Consumer starts waiting', flush=True)
        since = time.time_ns()
        with cond:
            print('Consumer condition entered', flush=True)
            while response is None:
                cond.wait()

            elapsed = (time.time_ns() - since) / 1_000_000
            print(f'Consumer got response "{response}" after {elapsed:.2f} ms', flush=True)
        print('Consumer condition exited', flush=True)

    threads = [threading.Thread(target=producer), threading.Thread(target=consumer)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
