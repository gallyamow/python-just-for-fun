import json
import threading
import random

from rabbit.channel import get_channel
from rabbit.topology import setup_topology

MAX_RETRY_COUNT = 2


def consumer_worker():
    conn, chan = get_channel()
    setup_topology(chan)

    # prefetch_count - сколько unacked сообщений можно держать «в работе»
    # prefetch_size - тоже самое, но ограничивает размером
    chan.basic_qos(prefetch_count=1)

    # bind callback
    chan.basic_consume(
        queue="main.queue",
        on_message_callback=callback
    )

    try:
        while not stop_event.is_set():
            # ручной способ consume, чтобы не использовать start_consuming - который блокирующий
            conn.process_data_events(time_limit=1)
    finally:
        chan.close()
        conn.close()


def callback(ch, method, properties, body):
    retry_count = get_retry_count(properties)

    payload = json.loads(body)

    if retry_count >= MAX_RETRY_COUNT:
        # При превышении количества повторов, публикуем в parking-обменник
        ch.basic_publish(
            exchange="parking.exchange",
            routing_key="parking",  # direct
            body=body,
            properties=properties
        )

        # Очень важно делать ack, иначе сообщение останется в DLE
        ch.basic_ack(method.delivery_tag)

        print(f'{threading.current_thread().name} parked after {retry_count} retries')

        return

    try:
        print(f'{threading.current_thread().name} received after {retry_count} retries', payload)

        handle_event(payload)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"{threading.current_thread().name} failed, retry {retry_count}", e)

        # nack без возврата в очередь (важно для dead-letter обработки)
        # (повтор через nack + requeue=true - самый простой способ, но неуправляемый)
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )


def handle_event(payload) -> bool:
    if random.random() < 0.3:
        raise Exception('something gone wrong')
    return True


def get_retry_count(properties) -> int:
    """
    Возвращает количество повторных доставок из заголовка x-death.
    Если заголовка нет — возвращает 0.
    """
    headers = getattr(properties, 'headers', None)
    if not headers:
        return 0

    x_death = headers.get('x-death')
    if not x_death or not isinstance(x_death, list):
        return 0

    # Берем первую запись в x-death, что соответствует последнему реальному циклу доставки.
    first_death = x_death[0]
    return first_death.get('count', 0)


# без daemon=True, так как сами ждем join
stop_event = threading.Event()

# @idiomatic: simple way to create threads
threads = [threading.Thread(target=consumer_worker, name=f"consumer-{i}") for i in range(10)]
for t in threads:
    t.start()

# @idiomatic: graceful shutdown + ctrl+c handling + ctrl+d (сигнал ввода больше не будет)
try:
    # Пока есть живые дочерние потоки
    while any(t.is_alive() for t in threads):
        for t in threads:
            # Блокирует главный поток на 0.5 сек в ожидании завершения дочернего. Если пользователь нажимает Ctrl+C во
            # время этого таймаута, Python генерирует KeyboardInterrupt прямо в главном потоке.
            # (используем этот подход вместо input())
            t.join(timeout=0.5)
except (KeyboardInterrupt, EOFError):
    print("\nStopping...")
    stop_event.set()
    for t in threads:
        # Здесь уже ждем без таймаута, так как точно знаем что завершаемся
        t.join()
