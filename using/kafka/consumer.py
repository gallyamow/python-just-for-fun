import json
import threading
import random
from confluent_kafka import Consumer

conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "events-group",
    "auto.offset.reset": "earliest",
    # обязательно отключаем autocommit
    "enable.auto.commit": False,
    # Увеличил лимиты. Но правильный способ: pool в одном потоке, затем обработка результата в worker pool
    "max.poll.interval.ms": 300000,
}


def consumer_worker():
    consumer = Consumer(conf)
    consumer.subscribe(
        ["events"],
        # on_revoke - нужен потому что многопоточный:
        # consumer может потерять partition
        # offset ещё не committed
        # другой consumer начнёт читать с прошлого offset
        # будут дубли
        on_revoke=on_revoke,
    )

    try:
        while not stop_event.is_set():
            # 1) Забирает сообщения из Kafka
            # 2) Отправляет heartbeat в consumer group
            # 3) Обрабатывает rebalance
            # 4)⃣ Возвращает одно сообщение или None
            # 5)️ Поддерживает offset-менеджмент
            # Ждем не более 1 секунды
            msg = consumer.poll(1.0)
            # ручной способ consume, чтобы не использовать start_consuming - который блокирующий
            if msg is None:
                continue
            if msg.error():
                continue

            event = json.loads(msg.value().decode())

            try:
                # long processing без защиты
                # Если handle_event() > max.poll.interval.ms => Kafka выкинет consumer из group и будет перебалансировка
                handle_event(event)

                # commit ПОСЛЕ успешной обработки
                consumer.commit(msg)
            except Exception as e:
                # retry / DLQ
                print("error:", e)
    finally:
        consumer.close()


def handle_event(payload) -> bool:
    if random.random() < 0.3:
        raise Exception("something gone wrong")
    print(payload)
    return True


def on_revoke(consumer, partitions):
    consumer.commit()


# без daemon=True, так как сами ждем join
stop_event = threading.Event()

# 1 поток делает poll
# 10 потоков ≠ 10x throughput
# максимум = число partition
# если partitions = 3, то 7 потоков будут idle
t = threading.Thread(target=consumer_worker, name="consumer-main")
t.start()

# @idiomatic: graceful shutdown + ctrl+c handling + ctrl+d (сигнал ввода больше не будет)
try:
    # Пока есть живые дочерние потоки
    while t.is_alive():
        # Блокирует главный поток на 0.5 сек в ожидании завершения дочернего. Если пользователь нажимает Ctrl+C во
        # время этого таймаута, Python генерирует KeyboardInterrupt прямо в главном потоке.
        # (используем этот подход вместо input())
        t.join(timeout=0.5)
except (KeyboardInterrupt, EOFError):
    print("\nStopping...")
    stop_event.set()
    # Здесь уже ждем без таймаута, так как точно знаем что завершаемся
    t.join()
