defmodule A2aAgentWebWeb.StatusControllerTest do
  @moduledoc """
  Tests for the /api/status health endpoint.
  """
  use A2aAgentWebWeb.ConnCase, async: true

  import Plug.Conn
  import Phoenix.ConnTest

  test "GET /api/status returns ok and time", %{conn: conn} do
    conn = get(conn, "/api/status")
    assert json_response(conn, 200)["status"] == "ok"
    assert is_binary(json_response(conn, 200)["time"])
  end
end
