defmodule A2AAgentWeb.WorkflowYAMELoader do
  @moduledoc """
  Loads and parses workflow definitions from YAML files into the internal graph structure
  compatible with the XCS engine. Intended for use with workflows defined in the YAML DSL.

  Example usage:
      {:ok, workflow} = A2AAgentWeb.WorkflowYAMELoader.load("workflows/summarize_and_analyze.yaml")
      # => %{nodes: [...], edges: [...]} (ready for XCS)
  """

  @type node_t :: %{id: atom(), op: atom(), params: map(), depends_on: [atom()] | nil}
  @type edge_t :: {atom(), atom()}
  @type workflow_t :: %{nodes: [node_t], edges: [edge_t]}

  @spec load(String.t()) :: {:ok, workflow_t} | {:error, term()}
  def load(path) do
    with {:ok, yaml} <- File.read(path),
         {:ok, data} <- YamlElixir.read_from_string(yaml) do
      IO.inspect(data, label: "YAML parsed data")
      case parse_workflow(data) do
        {:ok, workflow} -> {:ok, workflow}
        error -> error
      end
    else
      error -> {:error, error}
    end
  end

  @spec parse_workflow(map() | list()) :: {:ok, workflow_t} | {:error, term()}
  defp parse_workflow(%{"nodes" => nodes, "edges" => edges}) do
    parsed_nodes = Enum.map(nodes, &parse_node/1)
    parsed_edges = Enum.map(edges, &parse_edge/1)
    {:ok, %{nodes: parsed_nodes, edges: parsed_edges}}
  end
  defp parse_workflow(%{nodes: nodes, edges: edges}) do
    parsed_nodes = Enum.map(nodes, &parse_node/1)
    parsed_edges = Enum.map(edges, &parse_edge/1)
    {:ok, %{nodes: parsed_nodes, edges: parsed_edges}}
  end
  defp parse_workflow(list) when is_list(list) do
    parsed_nodes = Enum.map(list, &parse_node/1)
    {:ok, %{nodes: parsed_nodes, edges: []}}
  end
  defp parse_workflow(_), do: {:error, :invalid_yaml_structure}

  @spec parse_node(map()) :: node_t
  defp parse_node(node) do
    %{
      id: String.to_atom(node["id"]),
      op: String.to_atom(node["op"]),
      params: deep_atomize_keys(Map.get(node, "params", %{})),
      depends_on: (node["depends_on"] || []) |> Enum.map(&String.to_atom/1)
    }
  end

  @spec deep_atomize_keys(map() | any) :: map() | any
  defp deep_atomize_keys(%{} = map) do
    for {k, v} <- map, into: %{} do
      key = if is_binary(k), do: String.to_atom(k), else: k
      value = if is_map(v), do: deep_atomize_keys(v), else: v
      {key, value}
    end
  end
  defp deep_atomize_keys(other), do: other

  @spec parse_edge(String.t()) :: edge_t
  defp parse_edge(edge_str) do
    [from, to] = String.split(edge_str, "->") |> Enum.map(&String.trim/1) |> Enum.map(&String.to_atom/1)
    {from, to}
  end
end
