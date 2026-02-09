import pika
import json
import time


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print('received', data)

        time.sleep(2)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("error:", e)

        # nack без возврата в очередь
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )

# connect
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

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

channel.basic_qos(prefetch_count=1)

# bind callback
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback
)

print("Consumer waiting for messages...")

# start
channel.start_consuming()
