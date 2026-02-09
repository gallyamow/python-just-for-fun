import pika
import json
import time

# connect
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

# publish to exchange
for i in range(5):
    message = {
        "event_id": i,
        "type": "SOME_TYPE",
    }

    channel.basic_publish(
        exchange=exchange_name,
        routing_key="",  # для fanout не используется
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2  # persistent
        )
    )

    print("Sent:", message)
    time.sleep(1)

connection.close()
