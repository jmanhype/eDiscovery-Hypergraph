defmodule SampleAgentTest do
  use ExUnit.Case
  doctest HypergraphAgent.SampleAgent

  @moduledoc """
  Tests for the SampleAgent agent hooks with BasicOrchestrator.
  """

  defmodule OpEcho do
    @behaviour Operator
    def call(input), do: Map.put(input, "echoed", input["a"])
  end

  test "SampleAgent before_node increments input and after_node adds marker" do
    graph = %{n1: %{operator: OpEcho, deps: []}}
    agent_map = %{n1: HypergraphAgent.SampleAgent}
    input = %{"a" => 10}
    result = HypergraphAgent.BasicOrchestrator.orchestrate(graph, agent_map, input, [])
    assert result[:n1]["echoed"] == 11
    assert result[:n1]["agent_marker"] == "processed_n1"
  end

  test "BasicOrchestrator works with no agent hooks" do
    graph = %{n1: %{operator: OpEcho, deps: []}}
    agent_map = %{}
    input = %{"a" => 5}
    result = HypergraphAgent.BasicOrchestrator.orchestrate(graph, agent_map, input, [])
    assert result[:n1]["echoed"] == 5
    refute Map.has_key?(result[:n1], "agent_marker")
  end
end
