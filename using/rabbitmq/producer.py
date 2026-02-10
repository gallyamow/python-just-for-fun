import threading

from datetime import datetime
import pika
import json
import time


def publish_worker():
    # The primary rule for using Pika with threading is that you must have a separate BlockingConnection
    # instance within each thread, created in that thread
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = conn.channel()

    # build exchange
    exchange_name = 'some_exchange'
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type='fanout',
        durable=True
    )

    i = 0
    try:
        while not stop_event.is_set():
            message = {
                "event_id": i,
                "type": "time",
                "val": datetime.now().isoformat()
            }

            # publish to exchange
            channel.basic_publish(
                exchange=exchange_name,
                routing_key="",  # для fanout не используется
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # persistent
                )
            )

            print("Sent:", message)
            # time.sleep(0.1)
            i += 1
    finally:
        channel.close()
        conn.close()


# @idiomatic: graceful shutdown (даже несмотря на отсутствие wait)
stop_event = threading.Event()
t = threading.Thread(target=publish_worker)
t.start()

# @idiomatic: graceful shutdown + ctrl+c handling + ctrl+d (сигнал ввода больше не будет)
try:
    input("Press Enter to exit\n")
except (KeyboardInterrupt, EOFError):
    print("\nStopping...")

stop_event.set()
t.join()
