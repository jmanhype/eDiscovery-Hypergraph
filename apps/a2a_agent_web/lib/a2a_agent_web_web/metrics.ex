defmodule A2aAgentWebWeb.Metrics do
  @moduledoc """
  Prometheus metrics for A2A agent actions.
  """

  use Prometheus.Metric

  @doc """
  Declare and ensure all metrics are registered.
  """
  def setup do
    Counter.declare([
      name: :a2a_messages_total,
      help: "Total number of A2A messages received",
      labels: [:type]
    ])
    Counter.declare([
      name: :a2a_orchestrations_total,
      help: "Total number of orchestrations executed"
    ])
    Counter.declare([
      name: :a2a_negotiations_total,
      help: "Total number of negotiations",
      labels: [:result]
    ])
    Counter.declare([
      name: :a2a_errors_total,
      help: "Total number of error responses"
    ])
    Counter.declare([
      name: :a2a_errors_by_type_total,
      help: "Total number of error responses by type",
      labels: [:type]
    ])
    Summary.declare([
      name: :a2a_request_latency_seconds,
      help: "A2A API request latency (seconds)",
      labels: [:type]
    ])
    Summary.declare([
      name: :a2a_request_size_bytes,
      help: "A2A API request size (bytes)",
      labels: [:type]
    ])
  end

  def inc_message(type) do
    Counter.inc(name: :a2a_messages_total, labels: [type])
  end

  def inc_orchestration do
    Counter.inc(name: :a2a_orchestrations_total)
  end

  def inc_negotiation(result) do
    Counter.inc(name: :a2a_negotiations_total, labels: [result])
  end

  def inc_error do
    Counter.inc(name: :a2a_errors_total)
  end

  @doc """
  Increment error counter by error type.
  """
  def inc_error(type) do
    Counter.inc(name: :a2a_errors_by_type_total, labels: [type])
  end

  @doc """
  Observe request latency in seconds for a given type.
  """
  def observe_latency(type, latency) when is_binary(type) and is_number(latency) do
    Summary.observe([name: :a2a_request_latency_seconds, labels: [type]], latency)
  end

  @doc """
  Observe request size in bytes for a given type.
  """
  def observe_size(type, size) when is_binary(type) and is_integer(size) do
    Summary.observe([name: :a2a_request_size_bytes, labels: [type]], size)
  end
end
