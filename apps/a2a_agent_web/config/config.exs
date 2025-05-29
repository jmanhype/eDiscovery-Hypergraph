# OpenTelemetry configuration for exporting traces to a local collector (e.g., Jaeger, Tempo)
import Config

config :opentelemetry,
  tracer: :otlp_tracer,
  processors: [
    otel_batch_processor: %{
      exporter: {:opentelemetry_exporter, %{endpoints: ["http://localhost:4318"]}}
    }
  ]

config :a2a_agent_web, :nats,
  host: "nats",
  port: 4222
