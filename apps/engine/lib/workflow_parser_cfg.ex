defmodule WorkflowParserCFG do
  @moduledoc """
  NimbleParsec-based parser for strict validation of LLM workflow DSL.
  Accepts nodes with id, op, and optional depends_on, and edges.
  """
  import NimbleParsec

  # Helper parsers
  whitespace = ascii_string([?\s, ?\t, ?\n, ?\r], min: 0)
  id = ascii_string([?a..?z, ?A..?Z, ?0..?9, ?_], min: 1)
  op = ascii_string([?a..?z, ?A..?Z, ?0..?9, ?_], min: 1)
  key = ascii_string([?a..?z, ?A..?Z, ?0..?9, ?_], min: 1)
  quoted_string = ignore(string("\""))
    |> ascii_string([{:not, ?"}], min: 0)
    |> ignore(string("\""))
  number = integer(min: 1)

  param_value = choice([quoted_string, number])
  param_pair = ignore(string(", ")) |> concat(key |> tag(:key)) |> ignore(string(": ")) |> concat(param_value |> tag(:value))
  params = repeat(param_pair)

  depends_on =
    ignore(string(", depends_on: ["))
    |> repeat(id |> optional(ignore(string(", "))))
    |> ignore(string("]"))
    |> tag(:depends_on)

  node =
    ignore(whitespace)
    |> ignore(string("- id: "))
    |> concat(id |> tag(:id))
    |> ignore(string(", op: "))
    |> concat(op |> tag(:op))
    |> optional(depends_on)
    |> concat(params)
    |> reduce(:node_reducer)

  def not_quote(?", rest), do: {:halt, rest}
  def not_quote(char, rest), do: {[char], rest}


  nodes =
    ignore(string("Nodes:"))
    |> repeat(node)
    |> tag(:nodes)

  edge =
    ignore(whitespace)
    |> ignore(string("- "))
    |> concat(id |> tag(:from))
    |> ignore(string(" -> "))
    |> concat(id |> tag(:to))
    |> reduce(:edge_reducer)

  edges =
    ignore(string("Edges:"))
    |> repeat(edge)
    |> tag(:edges)

  workflow =
    nodes
    |> ignore(whitespace)
    |> concat(edges)
    |> ignore(whitespace)
    |> eos()

  defparsec :parse, workflow

  # Reducers for building Elixir maps
  def node_reducer(parts) do
    id = get_tag(parts, :id)
    op = get_tag(parts, :op)
    depends_on = get_tag(parts, :depends_on, []) |> Enum.map(&String.to_atom/1)
    # Only include key-value pairs in correct order
    params =
      parts
      |> Enum.chunk_every(2, 2, :discard)
      |> Enum.filter(fn
        [{:key, [_]}, {:value, [_]}] -> true
        _ -> false
      end)
      |> Enum.map(fn [{:key, [k]}, {:value, [v]}] -> {k, v} end)
    param_map = Map.new(params)
    [%{id: String.to_atom(id), op: String.to_atom(op), depends_on: depends_on, params: param_map}]
  end

  defp get_tag(parts, tag, default \\ nil) do
    case Enum.find(parts, fn {t, _} -> t == tag end) do
      {_, [v]} -> v
      {_, v} -> v
      nil -> default
    end
  end

  def edge_reducer([{:from, [from]}, {:to, [to]}]) do
    [%{from: String.to_atom(from), to: String.to_atom(to)}]
  end
end
