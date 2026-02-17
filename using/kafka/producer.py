import json
import threading
import time
from datetime import datetime
from confluent_kafka import Producer
import json


def publish_worker():
    # at least once - цель producer - не потерять сообщение при сбоях сети/брокера.
    # Поэтому:
    # - ждём подтверждение от всех ISR
    # - retry при ошибках
    # При превышении retry: сообщение считается FAILED: оно не записано в partition, offset не увеличился  consumer его никогда не увидит
    # Еще есть опция: delivery.timeout.ms - retry ещё есть, но timeout вышел
    producer = Producer({
        'bootstrap.servers': 'localhost:9092',
        'acks': 'all',
        'retries': 5,
        "delivery.timeout.ms": 300000,
        'linger.ms': 10,
        'enable.idempotence': True,  # защита от дубликатов на producer-стороне
    })

    i = 0
    try:
        while not stop_event.is_set():
            message = {
                "event_id": i,
                "type": "time",
                "val": datetime.now().isoformat()
            }

            producer.produce(
                topic='events',
                value=json.dumps(message).encode(), # требуется в байты
                on_delivery=delivery_report
            )

            # Для:
            # Обрабатывает delivery report callbacks (delivery_report)
            # Обрабатывает retry
            # Освобождает внутренние буферы
            # flush() тоже делает poll, но только в конце
            producer.pool(0)

            print("Sent:", message)
            i += 1
            time.sleep(0.1)
    finally:
        producer.flush()


def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed:", err)
    else:
        print("Delivered to", msg.topic(), msg.partition())


# @idiomatic: graceful shutdown (даже несмотря на отсутствие wait)
stop_event = threading.Event()
t = threading.Thread(target=publish_worker)
t.start()

# Здесь просто ожидание Enter для примера
input("Press Enter to exit\n")

stop_event.set()
t.join()
