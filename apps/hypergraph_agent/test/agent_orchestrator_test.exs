defmodule AgentOrchestratorTest do
  use ExUnit.Case
  doctest HypergraphAgent.AgentOrchestrator

  @moduledoc """
  Tests for the HypergraphAgent.AgentOrchestrator behaviour and BasicOrchestrator implementation.
  """

  defmodule OpAdd do
    @behaviour Operator
    def call(input), do: Map.put(input, "sum", Map.get(input, "a", 0) + Map.get(input, "b", 0))
  end
  defmodule OpMul do
    @behaviour Operator
    def call(input), do: Map.put(input, "prod", Map.get(input, "a", 1) * Map.get(input, "b", 1))
  end

  test "basic orchestrator runs graph with agent map" do
    graph = %{
      add: %{operator: OpAdd, deps: []},
      mul: %{operator: OpMul, deps: []}
    }
    agent_map = %{add: :agent1, mul: :agent2}
    input = %{"a" => 2, "b" => 3}
    result = HypergraphAgent.BasicOrchestrator.orchestrate(graph, agent_map, input, mode: :sequential)
    assert result[:add]["sum"] == 5
    assert result[:mul]["prod"] == 6
  end
end
