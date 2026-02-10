import random
import threading

import pika
import json
import time


def publish_worker():
    # Внутри worker: Connection и Channel должны использоваться в одном потоке
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

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
                "type": "SOME_TYPE",
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
            time.sleep(0.5)
            i += 1
    finally:
        connection.close()


stop_event = threading.Event()
t = threading.Thread(target=publish_worker)
t.start()

input('Press Enter to exit')

stop_event.set()
t.join()
