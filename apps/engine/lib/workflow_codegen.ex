defmodule WorkflowCodegen do
  @moduledoc """
  Generates Elixir modules for a workflow graph parsed from the DSL.
  Each node becomes a function; dependencies are respected in the generated execution order.
  """

  @doc """
  Given a workflow map (with :nodes and :edges), generates Elixir module source code as a string.
  """
  @spec generate_module(map()) :: String.t()
  def generate_module(%{nodes: nodes, edges: edges}) do
    node_defs = Enum.map(nodes, &node_function/1) |> Enum.join("\n\n")
    exec_body = exec_function_body(nodes, edges)
    """
defmodule GeneratedWorkflow do
  @moduledoc "Auto-generated workflow module."

#{node_defs}

  def run(input) do
#{exec_body}
  end
end
"""
  end

  # Generates a function for each node
  @spec node_function(map()) :: String.t()
  defp node_function(%{id: id, op: op, params: params}) do
    params_str = inspect(params, charlists: :as_lists)
    op_module_ast = Macro.camelize(Atom.to_string(op))
    """
  @doc "Node #{id} executes operation :#{op} with params #{String.replace(params_str, "\"", "'")}."
  @spec #{id}(map()) :: {:ok, any()}
  def #{id}(input) do
    # Calls the operator module's call/2 function
    operator = Module.concat([MyApp, Operators, #{op_module_ast}])
    case operator.call(input, #{params_str}) do
      {:ok, result} -> {:ok, result}
      {:error, reason} -> raise "Operator #{op} failed: \#{inspect(reason)}"
      other -> {:ok, other}
    end
  end
"""
  end

  # Generates the body of the run/1 function, respecting dependencies
  defp exec_function_body(nodes, edges) do
    order = topo_sort(nodes, edges)
    Enum.map(order, fn node_id ->
      "    { :ok, #{node_id}_out } = #{node_id}(input)"
    end)
    |> Enum.join("\n")
  end

  # Simple topological sort for execution order
  defp topo_sort(nodes, edges) do
    node_ids = Enum.map(nodes, & &1.id)
    deps = Enum.reduce(edges, %{}, fn %{from: from, to: to}, acc ->
      Map.update(acc, to, [from], &[from | &1])
    end)
    topo_sort_helper(node_ids, deps, [], MapSet.new())
  end

  defp topo_sort_helper([], _deps, acc, _visited), do: Enum.reverse(acc)
  defp topo_sort_helper(node_ids, deps, acc, visited) do
    {ready, not_ready} = Enum.split_with(node_ids, fn id ->
      Map.get(deps, id, []) |> Enum.all?(&(&1 in acc))
    end)
    case ready do
      [] -> acc ++ not_ready # fallback if cyclic
      _ -> topo_sort_helper(not_ready, deps, ready ++ acc, visited)
    end
  end
end
