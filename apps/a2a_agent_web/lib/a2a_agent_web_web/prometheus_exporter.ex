defmodule A2aAgentWebWeb.PrometheusExporter do
  @moduledoc """
  Plug wrapper for Prometheus.PlugExporter for Phoenix compatibility.
  Implements init/1 and call/2.
  """
  import Plug.Conn

  @spec init(opts :: any) :: any
  def init(opts), do: opts

  @spec call(conn :: Plug.Conn.t(), opts :: any) :: Plug.Conn.t()
  def call(conn, opts) do
    Prometheus.PlugExporter.call(conn, opts)
  end
end
