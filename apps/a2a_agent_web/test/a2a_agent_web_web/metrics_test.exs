defmodule A2aAgentWebWeb.MetricsTest do
  @moduledoc """
  Integration tests for Prometheus /metrics endpoint and metrics instrumentation.
  """

  use A2aAgentWebWeb.ConnCase, async: true

  @doc """
  Validates that the /metrics endpoint returns Prometheus metrics and that counters increment for A2A actions.
  """
  test "GET /metrics returns Prometheus metrics and increments on A2A POST", %{conn: conn} do
    # Trigger an A2A message to increment a counter
    conn = post(conn, "/api/a2a", %{
      "type" => "task_request",
      "sender" => "agent1",
      "recipient" => "agent2",
      "payload" => %{
        "graph" => %{"nodes" => [], "edges" => []},
        "agent_map" => %{},
        "input" => %{}
      }
    })
    assert json_response(conn, 200)["status"] == "ok"

    # Now check /metrics
    conn = get(recycle(conn), "/metrics")
    body = response(conn, 200)
    assert body =~ "a2a_messages_total"
    assert body =~ "task_request"
  end
end
defmodule A2aAgentWebWeb.MetricsTest do
  use A2aAgentWebWeb.ConnCase, async: true

  @doc """
  Validates that the /metrics endpoint returns Prometheus metrics and that counters increment for A2A actions.
  """
  test "GET /metrics returns Prometheus metrics and increments on A2A POST", %{conn: conn} do
    # Trigger an A2A message to increment a counter
    conn = post(conn, "/api/a2a", %{
      "type" => "task_request",
      "sender" => "agent1",
      "recipient" => "agent2",
      "payload" => %{
        "graph" => %{"nodes" => [], "edges" => []},
        "agent_map" => %{},
        "input" => %{}
      }
    })
    assert json_response(conn, 200)["status"] == "ok"

    # Now check /metrics
    conn = get(recycle(conn), "/metrics")
    body = response(conn, 200)
    assert body =~ "a2a_messages_total"
    assert body =~ "task_request"
  end
end
