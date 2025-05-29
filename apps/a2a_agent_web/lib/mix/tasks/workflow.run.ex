defmodule Mix.Tasks.Workflow.Run do
  @moduledoc """
  Runs a workflow defined in YAML via the XCS engine.

  ## Usage

      mix workflow.run PATH_TO_YAML [--input key1=val1,key2=val2] [--json '{...}'] [--output path.json]

  Examples:

      mix workflow.run workflows/summarize_and_analyze.yaml --input text="Elixir is awesome!"
      mix workflow.run workflows/summarize_and_analyze.yaml --json '{"text":"Elixir is awesome!"}' --output result.json
  """
  use Mix.Task

  @shortdoc "Run a workflow from YAML"

  @impl true
  def run(args) do
    Mix.Task.run("app.start")

    {yaml_path, opts} = parse_args(args)
    IO.puts("DEBUG: opts = #{inspect(opts)}")
    input =
      cond do
        opts[:json] -> parse_json(opts[:json])
        opts[:input] -> parse_input(opts[:input])
        true -> %{}
      end
    IO.puts("DEBUG: parsed input = #{inspect(input)}")

    IO.puts("DEBUG: YAML path: #{yaml_path}")
    IO.puts("DEBUG: File.exists?: #{File.exists?(yaml_path)}")
    case A2AAgentWeb.WorkflowYAMELoader.load(yaml_path) do
      {:ok, workflow} ->
        converted = convert_workflow(workflow)
        graph = workflow_to_graph(converted)
        result = Engine.run(graph, input)
        output_result(result, opts[:output])
      {:error, err} ->
        msg = "Workflow failed: #{inspect(err)}"
        Mix.shell().error(msg)
        IO.puts(msg)
    end
  end

  @doc """
  Converts a workflow map with string/atom keys to one with atom keys and values, but still in {:nodes, :edges} DSL format.
  """
  @spec convert_workflow(map()) :: %{nodes: list(map()), edges: list(tuple())}
  defp convert_workflow(%{"nodes" => nodes, "edges" => edges}), do: convert_workflow(%{nodes: nodes, edges: edges})
  defp convert_workflow(%{nodes: nodes, edges: edges}) do
    %{
      nodes: Enum.map(nodes, &convert_node/1),
      edges: Enum.map(edges, &convert_edge/1)
    }
  end

  @doc """
  Transforms a workflow DSL map (%{nodes: [...], edges: [...]}) into the graph map required by the engine.

  Each node is keyed by its :id, and dependencies are set from :depends_on or by analyzing edges.
  """
  @spec workflow_to_graph(%{nodes: list(map()), edges: list(tuple())}) :: map()
  defp workflow_to_graph(%{nodes: nodes, edges: edges}) do
    # Build a map of node_id => node_struct
    node_map =
      nodes
      |> Enum.map(fn node ->
        id = node[:id]
        deps =
          cond do
            Map.has_key?(node, :depends_on) -> node[:depends_on]
            true -> infer_node_deps(id, edges)
          end
        {
          id,
          %{
            operator: Map.fetch!(node, :op),
            params: atom_keys_to_strings(Map.get(node, :params, %{})),
            deps: deps
          }
        }
      end)
      |> Enum.into(%{})
    node_map
  end

  @doc """
  Infers dependencies for a node from the edges list if not explicitly set.
  """
  @spec infer_node_deps(atom(), list(tuple())) :: list(atom())
  defp infer_node_deps(node_id, edges) do
    edges
    |> Enum.filter(fn {from, to} -> to == node_id end)
    |> Enum.map(fn {from, _to} -> from end)
  end

  @doc """
  Recursively converts all atom keys in a map (or list of maps) to strings.
  """
  @spec atom_keys_to_strings(term()) :: term()
  defp atom_keys_to_strings(map) when is_map(map) do
    map
    |> Enum.map(fn {k, v} -> {to_string(k), atom_keys_to_strings(v)} end)
    |> Enum.into(%{})
  end
  defp atom_keys_to_strings(list) when is_list(list), do: Enum.map(list, &atom_keys_to_strings/1)
  defp atom_keys_to_strings(other), do: other


  defp convert_node(node) when is_map(node) do
    node
    |> Enum.map(fn {k, v} -> {string_to_atom(k), convert_node_value(string_to_atom(k), v)} end)
    |> Enum.into(%{})
  end

  defp convert_node_value(:depends_on, v) when is_list(v), do: Enum.map(v, &string_to_atom/1)
  @doc """
  Resolves an operator name (atom or string) to its full module reference.
  Example: "LLMOperator" -> A2aAgentWebWeb.Operators.LLMOperator
  """
  @spec resolve_operator(atom() | String.t()) :: module()
  defp resolve_operator(op) when is_atom(op) do
    resolve_operator(Atom.to_string(op))
  end
  defp resolve_operator(op) when is_binary(op) do
    Module.concat([A2aAgentWebWeb.Operators, Macro.camelize(op)])
  end

  defp convert_node_value(:op, v) when is_binary(v), do: resolve_operator(v)
  defp convert_node_value(:op, v) when is_atom(v), do: resolve_operator(v)
  defp convert_node_value(_k, v) when is_map(v), do: convert_node(v)
  defp convert_node_value(_k, v) when is_list(v), do: Enum.map(v, &convert_node_value(nil, &1))
  defp convert_node_value(_k, v), do: v

  defp convert_edge(edge) when is_tuple(edge), do: edge
  defp convert_edge(edge) when is_binary(edge) do
    [from, to] = String.split(edge, "->")
    {string_to_atom(from), string_to_atom(to)}
  end

  defp string_to_atom(val) when is_atom(val), do: val
  defp string_to_atom(val) when is_binary(val), do: String.to_atom(val)
  defp string_to_atom(val), do: val

  defp parse_args([yaml_path | rest]) do
    opts = Enum.chunk_every(rest, 2)
           |> Enum.reduce(%{}, fn
             ["--input", val], acc -> Map.put(acc, :input, val)
             ["--json", val], acc -> Map.put(acc, :json, val)
             ["--output", val], acc -> Map.put(acc, :output, val)
             _, acc -> acc
           end)
    {yaml_path, opts}
  end

  defp parse_input(str) do
    # Try to parse as JSON first
    case Jason.decode(str) do
      {:ok, map} when is_map(map) -> 
        map
      _ ->
        # Fall back to key=value pairs
        str
        |> String.split(",", trim: true)
        |> Enum.map(fn pair ->
          case String.split(pair, "=", parts: 2) do
            [k, v] -> {k, v}
            [k] -> {k, nil}
          end
        end)
        |> Enum.into(%{})
    end
  end

  defp parse_json(str) do
    case Jason.decode(str) do
      {:ok, map} when is_map(map) -> map
      _ -> Mix.raise("Invalid JSON input")
    end
  end

  defp output_result(result, nil) do
    IO.puts("Workflow result:")
    json = Jason.encode!(atom_keys_to_strings(result), pretty: true)
    IO.puts(json)
  end
  defp output_result(result, path) do
    json = Jason.encode!(atom_keys_to_strings(result), pretty: true)
    File.write!(path, json)
    IO.puts("Workflow result:")
    IO.puts(json)
    IO.puts("Result written to #{path}")
  end
end
