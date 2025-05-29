defmodule WorkflowParserCFGTest do
  @moduledoc """
  Tests for WorkflowParserCFG module using NimbleParsec.
  """
  use ExUnit.Case, async: true

  alias WorkflowParserCFG

  describe "parse/1" do
    test "parses valid workflow with dependencies" do
      llm_output = """
      Nodes:
      - id: step1, op: summarize
      - id: step2, op: analyze_sentiment, depends_on: [step1]
      - id: step3, op: decide, depends_on: [step2]
      Edges:
      - step1 -> step2
      - step2 -> step3
      """

      {:ok, [nodes: nodes, edges: edges], _, _, _, _} = WorkflowParserCFG.parse(llm_output)
      assert Enum.flat_map(nodes, & &1) == [
        %{id: :step1, op: :summarize, depends_on: []},
        %{id: :step2, op: :analyze_sentiment, depends_on: [:step1]},
        %{id: :step3, op: :decide, depends_on: [:step2]}
      ]
      assert Enum.flat_map(edges, & &1) == [
        %{from: :step1, to: :step2},
        %{from: :step2, to: :step3}
      ]
    end

    test "parses valid workflow with no dependencies" do
      llm_output = """
      Nodes:
      - id: a, op: foo
      - id: b, op: bar
      Edges:
      - a -> b
      """

      {:ok, [nodes: nodes, edges: edges], _, _, _, _} = WorkflowParserCFG.parse(llm_output)
      assert Enum.flat_map(nodes, & &1) == [
        %{id: :a, op: :foo, depends_on: []},
        %{id: :b, op: :bar, depends_on: []}
      ]
      assert Enum.flat_map(edges, & &1) == [
        %{from: :a, to: :b}
      ]
    end

    test "rejects malformed workflow" do
      malformed = "Nodes:\n- id: step1, op: summarize\nEdges:\n- step1 step2"
      assert {:error, _, _, _, _, _} = WorkflowParserCFG.parse(malformed)
    end
  end
end
