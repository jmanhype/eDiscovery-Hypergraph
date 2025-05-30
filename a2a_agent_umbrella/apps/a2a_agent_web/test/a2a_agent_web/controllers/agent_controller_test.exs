defmodule A2aAgentWeb.AgentControllerTest do
  use A2aAgentWeb.ConnCase, async: true

  @moduledoc """
  Tests for the /api/agent_card and /api/a2a endpoints.
  """

  describe "/api/agent_card" do
    test "GET returns agent card JSON", %{conn: conn} do
      conn = get(conn, "/api/agent_card")
      assert json_response(conn, 200)["id"] == "agent-123"
      assert json_response(conn, 200)["name"] == "Sample Elixir A2A Agent"
      assert is_list(json_response(conn, 200)["skills"])
    end
  end

  describe "/api/a2a" do
    @doc """
    POST /api/a2a with a valid graph, agent_map, and input triggers orchestration and returns a result.
    """
    test "POST valid A2A message triggers orchestration", %{conn: conn} do
      # Minimal graph: one node, no deps, operator is a simple echo operator
      graph = %{"n1" => %{operator: HypergraphAgent.SampleAgent, deps: []}}
      agent_map = %{"n1" => HypergraphAgent.SampleAgent}
      input = %{"a" => 1}
      msg = %{graph: graph, agent_map: agent_map, input: input}
      conn = post(conn, "/api/a2a", msg)
      body = json_response(conn, 200)
      assert body["status"] == "ok"
      assert is_map(body["result"])
      assert Map.has_key?(body["result"], "n1")
    end

    @doc """
    POST /api/a2a with missing required fields returns an error.
    """
    test "POST missing required fields returns error", %{conn: conn} do
      msg = %{foo: "bar"}
      conn = post(conn, "/api/a2a", msg)
      body = json_response(conn, 200)
      assert body["status"] == "error"
      assert body["error"] =~ "Missing required fields"
    end

    @doc """
    POST /api/a2a with an orchestrator error returns an error response.
    """
    test "POST with orchestrator error returns error", %{conn: conn} do
      # Use a graph that will fail (e.g., operator is not a module)
      graph = %{"n1" => %{operator: :not_a_module, deps: []}}
      agent_map = %{"n1" => :not_a_module}
      input = %{"a" => 1}
      msg = %{graph: graph, agent_map: agent_map, input: input}
      conn = post(conn, "/api/a2a", msg)
      body = json_response(conn, 200)
      assert body["status"] == "error"
      assert is_binary(body["error"])
    end
  end
end
