defmodule A2aAgentWebWeb.AgentControllerRegistryTest do
  @moduledoc """
  Integration tests for agent registry endpoints (register, unregister, get, list).
  """
  use A2aAgentWebWeb.ConnCase, async: false
  alias A2aAgentWebWeb.AgentCard

  setup do
    Agent.update(A2aAgentWebWeb.AgentRegistry, fn _ -> %{} end)
    :ok
  end

  @agent_card %{
    "id" => "agent42",
    "name" => "TestAgent",
    "version" => "1.0",
    "description" => "Test agent card",
    "capabilities" => ["foo", "bar"],
    "endpoints" => %{"a2a" => "/api/a2a"},
    "authentication" => nil
  }

  test "registers and gets agent card", %{conn: conn} do
    conn = post(conn, "/api/agent_card", @agent_card)
    assert json_response(conn, 200)["status"] == "ok"
    conn = get(build_conn(), "/api/agent_card/agent42")
    assert json_response(conn, 200)["id"] == "agent42"
  end

  test "lists agents after registration", %{conn: conn} do
    post(conn, "/api/agent_card", @agent_card)
    conn = get(build_conn(), "/api/agent_registry")
    agents = json_response(conn, 200)
    assert Enum.any?(agents, &(&1["id"] == "agent42"))
  end

  test "unregisters agent", %{conn: conn} do
    post(conn, "/api/agent_card", @agent_card)
    conn = delete(build_conn(), "/api/agent_card/agent42")
    assert json_response(conn, 200)["status"] == "ok"
    conn = get(build_conn(), "/api/agent_card/agent42")
    assert json_response(conn, 404)["status"] == "error"
  end

  test "unregistering non-existent agent returns 404", %{conn: conn} do
    conn = delete(build_conn(), "/api/agent_card/doesnotexist")
    resp = json_response(conn, 404)
    assert resp["status"] == "error"
    assert resp["error"] == "Agent not found"
    assert resp["id"] == "doesnotexist"
  end
end
