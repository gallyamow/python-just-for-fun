import json
import threading

import pika


def consumer_worker():
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = conn.channel()

    # build exchange
    exchange_name = 'some_exchange'
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type="fanout",
        durable=True
    )

    # build queue
    queue_name = "some_queue"
    channel.queue_declare(queue=queue_name, durable=True)

    # bind queue to channel
    channel.queue_bind(
        exchange=exchange_name,
        queue=queue_name
    )

    # prefetch_count - сколько unacked сообщений можно держать «в работе»
    # prefetch_size - тоже самое, но ограничивает размером
    channel.basic_qos(prefetch_count=1)

    # bind callback
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback)

    try:
        while not stop_event.is_set():
            # ручной способ consume, чтобы не использовать start_consuming - который блокирующий
            conn.process_data_events(time_limit=1)
    finally:
        channel.close()
        conn.close()


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f'{threading.current_thread().name} received', data)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("error:", e)

        # nack без возврата в очередь
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )


# без daemon=True, так как сами ждем join
stop_event = threading.Event()

# @idiomatic: simple way to create threads
threads = [threading.Thread(target=consumer_worker, name=f"consumer-{i}") for i in range(10)]
for t in threads:
    t.start()

# @idiomatic: graceful shutdown + ctrl+c handling + ctrl+d (сигнал ввода больше не будет)
try:
    input("Press Enter to exit\n")
except (KeyboardInterrupt, EOFError):
    print("\nStopping...")

stop_event.set()

for t in threads:
    t.join()
