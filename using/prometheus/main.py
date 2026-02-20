from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from datetime import datetime
from otel import setup_otel
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

setup_otel(service_name="fastapi-app")

"""
Есть общий стандарт Opentracing, который описывает как и что должно собираться, не привязываясь трассировкой 
к конкретной реализации в каком-либо языке.

На проде примерно расходует 2-5% CPU - с правильной настройкой.
В prometheus не видны span, он работает с числами.

Как они дополняют друг друга:
- Prometheus: ухудшились метрики, сервис тормозит.
- Jaeger: где конкретно тормозит

В примере используется Jaeger как имплементация Opentracing. Он работает так:
1) есть jaeger-agents в которые стоят на каждой машине, в него логируют все сервисы
2) есть jaeger-collector - в него все агенты посылают собранные трейсы, и он пишет их в БД
3) база данных - в jaeger при dev - badger (in-memory), на production используют cassandra или elasticsearch
4) jaeger-query - сервис который ходит в бд и селектит данные
5) jaeger-ui - веб интерфейс для поиска и просмотра трейсов, использует jaeger-query

METRICS:
  App ──(pull)──> Prometheus
TRACES:
  App ──(push/OTLP)──> Jaeger
LOGS:
  App ──> Loki / ELK (опционально)

# Запуск (хост важен для правильной работы с host.docker.internal)
fastapi dev main.py  --host 0.0.0.0 --port 8000
"""
app = FastAPI()

"""
Автоматически оборачивает весь FastAPI / Starlette pipeline:
- каждый HTTP request → span
- route → span
- status code
- latency
- исключения
- middleware
- async context

Получим такой корневой span:
HTTP GET /some_route
 ├─ framework=fastapi
 ├─ http.method=GET
 ├─ http.route=/some_route
 ├─ http.status_code=200
 └─ duration=523ms
"""
FastAPIInstrumentor.instrument_app(app)

"""
Автоматически инструментирует библиотеку requests.
Если в коде будет использоваться requests, то и эти вызовы будут со вложенным span. Причем связь с исходным - сохранится.
import requests
requests.get("https://api.example.com")
"""
RequestsInstrumentor().instrument()


class TimeOut(BaseModel):
    time: datetime


tracer = trace.get_tracer(__name__)


@app.get("/")
def index() -> HTMLResponse:
    content = """
    <html>
        <head>
            <title>index</title>
        </head>
        <body>
           <p>Links:</p>
           <ul>
            <li><a href="/time">time</a></li> 
            <li><a href="/traced_time">traced_time</a></li> 
            <li><a href="/some_unknown_url">404</a></li> 
            <li><a href="/metrics">metrics (8000) disabled</a></li> 
           </ul>
        </body>
    </html>
    """
    return HTMLResponse(content=content)


@app.get("/time")
def time() -> TimeOut:
    return TimeOut(time=datetime.now())


@app.get("/traced_time")
def traced_time() -> TimeOut:
    """
    Добавляем span, он содержит как служебные (например ID родительского span),так и пользовательские key-value данные.
    Далее:
    - span отправляется в collector
    - сохраняется в базу как только он завершил свое выполнение (в нашем случае в jaeger)
    В дальнейшем можно построить дерево всех span соединяя по id родителя.
    При анализе можно найти, например, все span в каком-то сервисе, которые заняли больше какого-то времени.
    Дальше, перейдя на конкретнyaый span, увидеть все дерево выше и ниже этого span.
    """

    with tracer.start_as_current_span("traced_time"):
        pass
    return TimeOut(time=datetime.now())

"""
Не требуется, так как используем MeterProvider в otel.
Иначе будут дубли.
"""
# @app.get("/metrics")
# def metrics():
#     return Response(
#         generate_latest(),
#         media_type=CONTENT_TYPE_LATEST
#     )
