defmodule Engine do
  @moduledoc """
  Hypergraph execution engine for multi-agent workflows.
  Supports graph-based operator execution with dependency resolution and parallelization.
  """

  @type node_id :: any()
  @type graph :: %{node_id() => %{operator: module(), deps: [node_id()]}}
  @type input :: map()
  @type output :: map()

  @doc """
  Runs the operator graph on the provided input.
  Supports sequential and parallel execution modes.

  ## Options
    - :mode - :sequential (default) or :parallel
  """
  @spec run(graph(), input(), keyword()) :: %{node_id() => output()}
  def run(graph, input, opts \\ []) do
    mode = Keyword.get(opts, :mode, :sequential)
    order = topo_sort(graph)
    case mode do
      :parallel -> exec_parallel(graph, order, input)
      _ -> exec_sequential(graph, order, input)
    end
  end

  @doc """
  Topologically sorts the graph nodes by dependencies.
  Returns a list of node_ids in execution order.
  """
  @spec topo_sort(graph()) :: [node_id()]
  def topo_sort(graph) do
    nodes = Map.keys(graph)
    visited = MapSet.new()
    Enum.reduce(nodes, {[], visited}, fn node, {acc, vis} ->
      visit(node, graph, acc, vis)
    end)
    |> elem(0)
    |> Enum.reverse()
  end

  defp visit(node, graph, acc, visited) do
    if MapSet.member?(visited, node) do
      {acc, visited}
    else
      {acc, vis} =
        Enum.reduce(graph[node][:deps] || [], {acc, visited}, fn dep, {a, v} ->
          visit(dep, graph, a, v)
        end)
      {[node | acc], MapSet.put(vis, node)}
    end
  end

  @doc """
  Executes the graph sequentially by topological order.
  """
  @spec exec_sequential(graph(), [node_id()], input()) :: %{node_id() => output()}
  def exec_sequential(graph, order, input) do
    Enum.reduce(order, %{}, fn node, acc ->
      op = graph[node][:operator]
      spec = Map.get(graph[node], :specification)
      dep_outputs = Enum.map(graph[node][:deps], &acc[&1])
      node_params = Map.get(graph[node], :params, %{})
      
      # For root nodes (no dependencies), merge workflow input with params
      base_input = if dep_outputs == [], do: input, else: %{}
      
      node_input =
        base_input
        |> Map.merge(node_params)
        |> Map.merge(Enum.reduce(dep_outputs, %{}, &Map.merge(&2, &1)))
      validated_input =
        case spec do
          nil -> node_input
          spec_mod ->
            case spec_mod.validate_input(node_input) do
              :ok -> node_input
              {:error, reason} -> raise "Input validation failed for node #{inspect(node)}: #{inspect(reason)}"
            end
        end
      node_output = op.call(validated_input) |> unwrap_ok_and_wrap_map()
      _ =
        case spec do
          nil -> :ok
          spec_mod ->
            case spec_mod.validate_output(node_output) do
              :ok -> :ok
              {:error, reason} -> raise "Output validation failed for node #{inspect(node)}: #{inspect(reason)}"
            end
        end
      Map.put(acc, node, node_output)
    end)
  end

  @doc """
  Unwraps {:ok, value} to value, and wraps non-map values as %{result: value} for engine merging.
  """
  @spec unwrap_ok_and_wrap_map(any()) :: map()
  defp unwrap_ok_and_wrap_map({:ok, value}), do: unwrap_ok_and_wrap_map(value)
  defp unwrap_ok_and_wrap_map(map) when is_map(map), do: map
  defp unwrap_ok_and_wrap_map(other), do: %{result: other}

  @doc """
  Executes the graph in parallel by levels (nodes with no dependencies run together).
  """
  @spec exec_parallel(graph(), [node_id()], input()) :: %{node_id() => output()}
  def exec_parallel(graph, order, input) do
    levels = group_by_level(graph, order)
    Enum.reduce(levels, %{}, fn level, acc ->
      tasks = for node <- level do
        Task.async(fn ->
          op = graph[node][:operator]
          spec = Map.get(graph[node], :specification)
          dep_outputs = Enum.map(graph[node][:deps], &acc[&1])
          node_params = Map.get(graph[node], :params, %{})
          
          # For root nodes (no dependencies), merge workflow input with params
          base_input = if dep_outputs == [], do: input, else: %{}
          
          node_input =
            base_input
            |> Map.merge(node_params)
            |> Map.merge(Enum.reduce(dep_outputs, %{}, &Map.merge(&2, &1)))
          validated_input =
            case spec do
              nil -> node_input
              spec_mod ->
                case spec_mod.validate_input(node_input) do
                  :ok -> node_input
                  {:error, reason} -> raise "Input validation failed for node #{inspect(node)}: #{inspect(reason)}"
                end
            end
          node_output = op.call(validated_input) |> unwrap_ok_and_wrap_map()
          _ =
            case spec do
              nil -> :ok
              spec_mod ->
                case spec_mod.validate_output(node_output) do
                  :ok -> :ok
                  {:error, reason} -> raise "Output validation failed for node #{inspect(node)}: #{inspect(reason)}"
                end
            end
          {node, node_output}
        end)
      end
      results = Task.await_many(tasks)
      Enum.into(results, acc)
    end)
  end

  @doc """
  Groups nodes by level for parallel execution (nodes with same dependency depth).
  """
  @spec group_by_level(graph(), [node_id()]) :: [[node_id()]]
  def group_by_level(graph, order) do
    Enum.reduce(order, %{}, fn node, acc ->
      depth = max_dep_depth(graph, node)
      Map.update(acc, depth, [node], &[node | &1])
    end)
    |> Enum.sort_by(fn {d, _} -> d end)
    |> Enum.map(fn {_, nodes} -> Enum.reverse(nodes) end)
  end

  defp max_dep_depth(graph, node) do
    case graph[node][:deps] do
      [] -> 0
      deps ->
        depths = Enum.map(deps, &max_dep_depth(graph, &1))
        Enum.max(depths) + 1
    end
  end
end
