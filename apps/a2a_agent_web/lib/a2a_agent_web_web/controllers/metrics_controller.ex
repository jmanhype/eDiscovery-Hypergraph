defmodule A2aAgentWebWeb.MetricsController do
  @moduledoc """
  Controller to expose Prometheus metrics at /metrics endpoint.
  """
  use A2aAgentWebWeb, :controller

  @doc """
  Returns all Prometheus metrics in text format for Prometheus scraping.
  """
  @spec metrics(Plug.Conn.t(), map) :: Plug.Conn.t()
  def metrics(conn, _params) do
    metrics = Prometheus.Format.Text.format()
    conn
    |> put_resp_content_type("text/plain")
    |> send_resp(200, metrics)
  end
end
