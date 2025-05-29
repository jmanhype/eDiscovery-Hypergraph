defmodule A2aAgentWebWeb.StatusController do
  @moduledoc """
  Health and status controller for liveness/readiness checks.
  """
  use A2aAgentWebWeb, :controller

  @doc """
  Returns a JSON status response for health checks.
  """
  @spec status(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def status(conn, _params) do
    json(conn, %{status: "ok", time: DateTime.utc_now() |> DateTime.to_iso8601()})
  end
end
