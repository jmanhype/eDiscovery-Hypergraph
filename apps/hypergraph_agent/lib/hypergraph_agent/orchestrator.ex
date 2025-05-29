defmodule HypergraphAgent.AgentOrchestrator do
  @moduledoc """
  Behaviour for orchestrating agent execution over a hypergraph operator graph.
  Agents may be assigned to nodes and can observe/modify node input/output using hooks.
  """

  @type agent_id :: any()
  @type node_id :: any()
  @type graph :: %{node_id() => %{operator: module(), deps: [node_id()]}}
  @type input :: map()
  @type output :: map()
  @type agent_map :: %{node_id() => agent_id()}

  @callback orchestrate(graph(), agent_map(), input(), keyword()) :: %{node_id() => output()}
  @callback before_node(node_id(), input(), module(), map()) :: input()
  @callback after_node(node_id(), output(), module(), map()) :: output()
  @optional_callbacks before_node: 4, after_node: 4
end

defmodule HypergraphAgent.BasicOrchestrator do
  @moduledoc """
  Sample orchestrator that assigns agents to nodes and coordinates execution via Engine.
  Supports agent hooks: before_node/4 and after_node/4.
  """
  @behaviour HypergraphAgent.AgentOrchestrator

  @impl true
  @spec orchestrate(
          HypergraphAgent.AgentOrchestrator.graph(),
          HypergraphAgent.AgentOrchestrator.agent_map(),
          HypergraphAgent.AgentOrchestrator.input(),
          keyword()
        ) :: %{HypergraphAgent.AgentOrchestrator.node_id() => HypergraphAgent.AgentOrchestrator.output()}
  require Logger
  def orchestrate(graph, agent_map, input, _opts \\ []) do
    try do
      order = Engine.topo_sort(graph)
      result = Enum.reduce(order, %{}, fn node, acc ->
        agent = Map.get(agent_map, node)
        node_data = graph[node] || %{}
        op = node_data[:operator]
        deps = node_data[:deps] || []
        dep_outputs = Enum.map(deps, &acc[&1])
        node_input = Map.merge(input, Enum.reduce(dep_outputs, %{}, &Map.merge(&2, &1)))
        # Agent before_node hook
        node_input2 =
          if agent && function_exported?(agent, :before_node, 4) do
            agent.before_node(node, node_input, op, acc)
          else
            node_input
          end
        # Operator call
        node_output =
          if is_nil(op) or not function_exported?(op, :call, 1) do
            Logger.error("Operator missing or invalid for node #{inspect(node)}: #{inspect(op)}")
            %{error: "invalid_operator", node: node}
          else
            op.call(node_input2)
          end
        # Agent after_node hook
        node_output2 =
          if agent && function_exported?(agent, :after_node, 4) do
            agent.after_node(node, node_output, op, acc)
          else
            node_output
          end
        Map.put(acc, node, node_output2)
      end)
      cond do
        is_map(result) -> {:ok, result}
        is_list(result) -> {:ok, Enum.into(result, %{})}
        is_nil(result) -> {:error, :nil_result}
        is_atom(result) -> {:error, result}
        true -> {:error, {:unexpected_result, result}}
      end
    rescue
      e ->
        Logger.error("Orchestrator error: #{inspect(e)}\n" <> Exception.format(:error, e, __STACKTRACE__))
        {:error, {:exception, e}}
    end
  end

end
