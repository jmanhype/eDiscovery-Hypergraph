defmodule WorkflowParser do
  @moduledoc """
  Parses LLM-generated workflow text into a workflow graph structure.
  Example input:

      Nodes:
      - id: step1, op: summarize
      - id: step2, op: analyze_sentiment, depends_on: [step1]
      - id: step3, op: decide, depends_on: [step2]
      Edges:
      - step1 -> step2
      - step2 -> step3
  """

  @node_regex ~r/- id: (\w+), op: (\w+)(?:, depends_on: \[(.*?)\])?/
  @edge_regex ~r/- (\w+) -> (\w+)/

  @spec parse(String.t()) :: %{nodes: list(map()), edges: list(map())}
  def parse(text) do
    nodes =
      Regex.scan(@node_regex, text)
      |> Enum.map(fn
        [_, id, op] ->
          %{id: String.to_atom(id), op: String.to_atom(op), depends_on: []}
        [_, id, op, depends_on] ->
          %{
            id: String.to_atom(id),
            op: String.to_atom(op),
            depends_on:
              depends_on
              |> to_string()
              |> String.split(",", trim: true)
              |> Enum.map(&String.trim/1)
              |> Enum.reject(&(&1 == ""))
              |> Enum.map(&String.to_atom/1)
          }
      end)

    edges =
      Regex.scan(@edge_regex, text)
      |> Enum.map(fn [_, from, to] ->
        %{from: String.to_atom(from), to: String.to_atom(to)}
      end)

    %{nodes: nodes, edges: edges}
  end
end
