defmodule A2aAgentWebWeb.SimulationController do
  @moduledoc """
  Handles simulation of LLM-generated workflow graphs.
  """
  use A2aAgentWebWeb, :controller

  alias Engine
  alias WorkflowParser

  @doc """
  Simulates a workflow graph based on the provided workflow text and input.
  """
  def simulate(conn, %{"workflow_text" => workflow_text, "input" => input}) do
    # Parse and validate the workflow
    parsed = WorkflowParser.parse(workflow_text)
    IO.inspect(parsed, label: "Parsed workflow")

    case parsed do
      %{nodes: nodes, edges: edges} = _graph when is_list(nodes) and is_list(edges) ->
        graph =
          nodes
          |> Enum.map(fn node ->
            IO.inspect(node.op, label: "Parsed node.op")

            operator_mod =
              try do
                normalize_operator(node.op)
              rescue
                e ->
                  IO.inspect({:bad_operator, node.op, e}, label: "Operator mapping error")
                  raise e
              end

            IO.inspect(operator_mod, label: "Mapped operator module")

            {node.id,
             %{
               operator: operator_mod,
               deps: Map.get(node, :depends_on, []),
               params:
                 Map.get(node, :params, %{})
                 |> Enum.into(%{}, fn
                   {k, v} when is_atom(k) -> {Atom.to_string(k), v}
                   pair -> pair
                 end)
                 |> Map.update("context", %{}, fn
                   ctx when is_binary(ctx) ->
                     case Jason.decode(ctx) do
                       {:ok, map} when is_map(map) -> map
                       _ -> %{}
                     end
                   ctx when is_map(ctx) -> ctx
                   _ -> %{}
                 end)
                 |> Map.update("prompt_template", "", & &1)
             }}
          end)
          |> Enum.map(fn {id, params} -> {id, params} end)
          |> Map.new()

        result = Engine.run(graph, input: input)
        json(conn, %{status: "ok", result: result})

      _ ->
        conn
        |> put_status(:bad_request)
        |> json(%{status: "error", error: "Invalid workflow format"})
    end
  end

  @doc false
  # Normalizes operator identifiers to their module implementations.
  defp normalize_operator(op) when is_binary(op) do
    case String.trim(String.downcase(op)) do
      "llm" -> A2aAgentWebWeb.Operators.LLMOperator
      "map" -> A2aAgentWebWeb.Operators.MapOperator
      "sequence" -> A2aAgentWebWeb.Operators.SequenceOperator
      "parallel" -> A2aAgentWebWeb.Operators.ParallelOperator
      "branch" -> A2aAgentWebWeb.Operators.BranchOperator
      "aggregate" -> A2aAgentWebWeb.Operators.AggregateOperator
      "pass_through" -> A2aAgentWebWeb.Operators.PassThroughOperator
      other -> raise "Unknown operator: #{inspect(other)}"
    end
  end

  defp normalize_operator(op) when is_atom(op), do: normalize_operator(Atom.to_string(op))
end