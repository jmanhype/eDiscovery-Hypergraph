defmodule A2aAgentWeb.AgentController do
  use A2aAgentWeb, :controller

  @moduledoc """
  Controller for A2A agent endpoints: /agent_card and /a2a.
  """

  # Example agent card. In a real system, this could be dynamic/configurable.
  @agent_card %{
    id: "agent-123",
    name: "Sample Elixir A2A Agent",
    skills: ["math", "reasoning"],
    endpoints: ["/a2a"],
    auth: nil
  }

  @doc """
  Returns the agent card as JSON.
  """
  def agent_card(conn, _params) do
    json(conn, @agent_card)
  end

  @doc """
  Receives an A2A message (POST /a2a).
  Expects a JSON body with keys: "graph", "agent_map", "input" (all maps).
  Invokes the orchestrator and returns the result or error.
  """
  def a2a(conn, %{"graph" => graph, "agent_map" => agent_map, "input" => input} = params) when is_map(graph) and is_map(agent_map) and is_map(input) do
    try do
      # Call orchestrator (adjust module path if needed)
      result = HypergraphAgent.BasicOrchestrator.orchestrate(graph, agent_map, input, [])
      json(conn, %{result: result, status: "ok"})
    rescue
      e ->
        json(conn, %{error: Exception.message(e), status: "error"})
    end
  end
  def a2a(conn, _params) do
    json(conn, %{error: "Missing required fields: graph, agent_map, input", status: "error"})
  end
end
