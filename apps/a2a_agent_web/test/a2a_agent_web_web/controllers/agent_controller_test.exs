defmodule A2aAgentWebWeb.AgentControllerTest do
  use A2aAgentWebWeb.ConnCase, async: true

  @moduletag :a2a

  describe "/api/agent_card" do
    test "GET returns agent metadata", %{conn: conn} do
      conn = get(conn, "/api/agent_card")
      assert json_response(conn, 200)["name"] == "A2A Agent"
    end
  end

  describe "/api/a2a" do
    test "POST valid A2A message triggers orchestration", %{conn: conn} do
      body = %{
        "type" => "task_request",
        "sender" => "agent1",
        "recipient" => "agent2",
        "payload" => %{
          "graph" => %{"nodes" => [], "edges" => []},
          "agent_map" => %{},
          "input" => %{}
        }
      }
      conn = post(conn, "/api/a2a", body)
      assert json_response(conn, 200)["status"] in ["ok", "error"]
    end

    setup do
      # Ensure at least one agent is registered before each test
      agent_card = A2aAgentWebWeb.AgentCard.build()
      A2aAgentWebWeb.AgentRegistry.register_agent(agent_card)
      :ok
    end

    test "POST agent_discovery returns agent list", %{conn: conn} do
      body = %{
        "type" => "agent_discovery",
        "sender" => "agent1",
        "recipient" => "agent2",
        "payload" => %{}
      }
      conn = post(conn, "/api/a2a", body)
      resp = json_response(conn, 200)
      assert resp["status"] == "ok"
      assert is_list(resp["agents"])
      assert Enum.any?(resp["agents"], &(&1["id"] == "agent1"))
    end

    test "POST negotiation returns accepted for valid proposal", %{conn: conn} do
      body = %{
        "type" => "negotiation",
        "sender" => "agent1",
        "recipient" => "agent2",
        "payload" => %{"proposal" => "foo bar", "details" => %{}}
      }
      conn = post(conn, "/api/a2a", body)
      resp = json_response(conn, 200)
      assert resp["status"] == "accepted"
      assert resp["reason"] =~ "accepted"
    end

    test "POST negotiation returns rejected for invalid proposal", %{conn: conn} do
      body = %{
        "type" => "negotiation",
        "sender" => "agent1",
        "recipient" => "agent2",
        "payload" => %{"proposal" => "bar", "details" => %{}}
      }
      conn = post(conn, "/api/a2a", body)
      resp = json_response(conn, 200)
      assert resp["status"] == "rejected"
      assert resp["reason"] =~ "rejected"
    end

    test "POST negotiation returns rejected for missing proposal", %{conn: conn} do
      body = %{
        "type" => "negotiation",
        "sender" => "agent1",
        "recipient" => "agent2",
        "payload" => %{"details" => %{}}
      }
      conn = post(conn, "/api/a2a", body)
      resp = json_response(conn, 200)
      assert resp["status"] == "rejected"
      assert resp["reason"] =~ "Invalid negotiation payload"
    end

    test "POST missing required fields returns error", %{conn: conn} do
      conn = post(conn, "/api/a2a", %{"foo" => "bar"})
      assert json_response(conn, 400)["status"] == "error"
    end
  end
end
