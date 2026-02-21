import json
import threading
import time
from datetime import datetime
from rabbit.channel import get_channel
from rabbit.topology import setup_topology
import pika


# Гарантии доставки:
# 1) at most once - если используется auto-ack и consumer падает после получения либо сеть после получения
# 2) at least once - если manual ack - basic.ack (чаще всего на проде). Если consumer падает - то возвращается в очередь.
# Но, может прийти и несколько раз => consumer должен быть идемпотентным.
#
# Итого: RabbitMQ чаще всего используют с at least once доставкой через manual acknowledgements.
def publish_worker():
    conn, chan = get_channel()
    setup_topology(chan)

    i = 0
    try:
        while not stop_event.is_set():
            message = {"event_id": i, "type": "time", "val": datetime.now().isoformat()}

            chan.basic_publish(
                exchange="main.exchange",
                routing_key="",  # для fanout не используется
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # persistent
                ),
            )

            print("Sent:", message)
            i += 1
            time.sleep(0.1)
    finally:
        chan.close()
        conn.close()


# @idiomatic: graceful shutdown (даже несмотря на отсутствие wait)
stop_event = threading.Event()
t = threading.Thread(target=publish_worker)
t.start()

# Здесь просто ожидание Enter для примера
input("Press Enter to exit\n")

stop_event.set()
t.join()
