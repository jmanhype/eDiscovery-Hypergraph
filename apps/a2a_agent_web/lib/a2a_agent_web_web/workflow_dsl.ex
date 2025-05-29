defmodule A2AAgentWeb.WorkflowDSL do
  @moduledoc """
  Macro-based DSL for defining operator workflows in Elixir.
  Expands to a workflow graph structure compatible with the XCS engine.
  Example usage:

      import A2AAgentWeb.WorkflowDSL
      workflow do
        node :summarize, LLMOperator, prompt_template: "Summarize: ~s", context: [topic: "Elixir DSLs"]
        node :analyze, MapOperator, depends_on: [:summarize], function: &MyApp.Analytics.analyze/1
      end
  """

  defmacro workflow(do: block) do
    quote do
      nodes = []
      edges = []
      import unquote(__MODULE__), only: [node: 2, node: 3]
      unquote(block)
      %{nodes: Enum.reverse(nodes), edges: Enum.reverse(edges)}
    end
  end

  defmacro node(id, op, opts \\ []) do
    quote bind_quoted: [id: id, op: op, opts: opts] do
      node = %{id: id, op: op, opts: opts}
      nodes = [node | (Module.get_attribute(__MODULE__, :nodes) || [])]
      Module.put_attribute(__MODULE__, :nodes, nodes)
      if Keyword.has_key?(opts, :depends_on) do
        Enum.each(List.wrap(opts[:depends_on]), fn dep ->
          edge = {dep, id}
          edges = [edge | (Module.get_attribute(__MODULE__, :edges) || [])]
          Module.put_attribute(__MODULE__, :edges, edges)
        end)
      end
    end
  end
end
