import pika

# Требования:
# 1) рассылка событий всем consumers и ожидание подтверждения от всех.
# 2) в случае если кто-то подтверждает пересылаем глобально всем.
# 3) делается повторное подтверждение
def setup_topology(chan: pika.adapters.blocking_connection.BlockingChannel):
    # Главный обменник рассылает события на обработку во все consumers.
    # Используем fanout, по требованиям.
    chan.exchange_declare(
        exchange="main.exchange",
        exchange_type="fanout",
        durable=True
    )

    # Retry-обменник для повторов с ttl
    chan.exchange_declare(
        exchange="retry.exchange",
        exchange_type="direct",
        durable=True
    )

    # Parking-обменник для пересылки окончательно failed
    chan.exchange_declare(
        exchange="parking.exchange",
        exchange_type="direct",
        durable=True
    )

    # Главная очередь
    chan.queue_declare(
        queue="main.queue",
        durable=True,
        arguments={
            # Повторы реализованы через указание  dead-letter-exchange у queue.
            # Туда отправляются dead-letter это когда: basic_nack(requeue=False) or basic_reject(requeue=False) or по TTL or очередь переполнена и есть max-length.
            # dead-letter - оправляем в обменник retry.exchange c routing key = "retry"
            # routing-key тут нужен, потому что этот обменник direct и он будет пересылать в queue равный по названию этому routing kye.
            # т.е. retry.exchange -> retry.queue
            "x-dead-letter-exchange": "retry.exchange",
            "x-dead-letter-routing-key": "retry",
        }
    )

    # Retry-очередь
    # Эта очередь, из-за того что ее никто не читает и из-за того что задано ttl будет пересылать сообщения в свою dead-letter exchange.
    # И благодаря тому что тут x-dead-letter-exchange равен главному exchange, они будут попадать на повторное исполнение с задержкой,
    # (в отличии, от просто nack + requeue=true - который будет повторять мгновенно и бесконечно).
    chan.queue_declare(
        queue="retry.queue",
        durable=True,
        arguments={
            "x-message-ttl": 10000,
            "x-dead-letter-exchange": "main.exchange",
            "x-dead-letter-routing-key": "main",
        }
    )

    # Parking-очередь для пересылки окончательно failed
    chan.queue_declare(
        queue="parking.queue",
        durable=True
    )

    # Привязка queue к exchanges
    chan.queue_bind(
        exchange="main.exchange",
        queue="main.queue",
        routing_key="main"
    )

    chan.queue_bind(
        exchange="retry.exchange",
        queue="retry.queue",
        routing_key="retry"
    )

    chan.queue_bind(
        exchange="parking.exchange",
        queue="parking.queue",
        routing_key="parking"
    )
