defmodule WorkflowCodegenExample do
  @moduledoc """
  Example usage of WorkflowCodegen to generate an Elixir module from a workflow graph.
  Run `WorkflowCodegenExample.demo/0` in IEx to see the generated code with real operator calls.
  """

  @doc """
  Generates and prints Elixir code for a sample workflow graph.
  The generated code will call operator modules like MyApp.Operators.Summarize, AnalyzeSentiment, and Decide.
  """
  @spec demo() :: :ok
  def demo do
    workflow = %{
      nodes: [
        %{id: :step1, op: :summarize, params: %{prompt: "Summarize this text."}},
        %{id: :step2, op: :analyze_sentiment, params: %{}},
        %{id: :step3, op: :decide, params: %{threshold: 0.5}}
      ],
      edges: [
        %{from: :step1, to: :step2},
        %{from: :step2, to: :step3}
      ]
    }

    code = WorkflowCodegen.generate_module(workflow)
    IO.puts("\nGenerated Elixir module with operator calls:\n")
    IO.puts(code)
    :ok
  end
end
