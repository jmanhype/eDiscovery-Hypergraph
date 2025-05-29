defmodule WorkflowParserTest do
  @moduledoc """
  Tests for WorkflowParser module.
  """
  use ExUnit.Case, async: true

  describe "parse/1" do
    test "parses nodes and edges from LLM output" do
      llm_output = """
      Nodes:
      - id: step1, op: summarize
      - id: step2, op: analyze_sentiment, depends_on: [step1]
      - id: step3, op: decide, depends_on: [step2]
      Edges:
      - step1 -> step2
      - step2 -> step3
      """

      expected = %{
        nodes: [
          %{id: :step1, op: :summarize, depends_on: []},
          %{id: :step2, op: :analyze_sentiment, depends_on: [:step1]},
          %{id: :step3, op: :decide, depends_on: [:step2]}
        ],
        edges: [
          %{from: :step1, to: :step2},
          %{from: :step2, to: :step3}
        ]
      }

      assert WorkflowParser.parse(llm_output) == expected
    end

    test "parses nodes with no dependencies" do
      llm_output = """
      Nodes:
      - id: a, op: foo
      - id: b, op: bar
      Edges:
      - a -> b
      """

      expected = %{
        nodes: [
          %{id: :a, op: :foo, depends_on: []},
          %{id: :b, op: :bar, depends_on: []}
        ],
        edges: [
          %{from: :a, to: :b}
        ]
      }

      assert WorkflowParser.parse(llm_output) == expected
    end
  end
end
