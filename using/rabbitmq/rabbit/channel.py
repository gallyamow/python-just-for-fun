import pika

from .connection import get_connection


def get_channel() -> (pika.BlockingConnection, pika.adapters.blocking_connection.BlockingChannel):
    conn = get_connection()
    chan = conn.channel()
    return conn, chan
