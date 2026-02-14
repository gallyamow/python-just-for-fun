import pika

# The primary rule for using Pika with threading is that you must have a separate BlockingConnection
# instance within each thread, created in that thread
def get_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
