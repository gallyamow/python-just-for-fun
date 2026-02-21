from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import start_http_server


def setup_otel(service_name: str):
    resource = Resource.create({"service.name": service_name})

    # traces
    """
    На проде включют:
    - sampling
    - настраивают BatchSpanProcessor.max_queue_size и schedule_delay_millis
    """
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
    )

    # metrics
    """
    OpenTelemetry сам поднимает /metrics
    endpoint регистрируется на уровне ASGI
    FastAPI ничего не знает про него
    Prometheus просто делает scrape
    """
    metric_reader = PrometheusMetricReader()
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # поднимаем /metric на другом порту (стандартном для otel)
    start_http_server(9464)
