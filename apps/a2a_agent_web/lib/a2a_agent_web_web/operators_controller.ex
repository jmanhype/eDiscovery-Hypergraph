defmodule A2aAgentWebWeb.OperatorsController do
  @moduledoc """
  Controller for operator introspection endpoints.
  Lists available operators and details for each.
  """
  use A2aAgentWebWeb, :controller

  @doc """
  Lists all available operator modules.
  """
  @spec index(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def index(conn, _params) do
    operators = [
      "aggregate_operator",
      "branch_operator",
      "llm_operator",
      "map_operator",
      "parallel_operator",
      "sequence_operator"
    ]
    json(conn, %{operators: operators})
  end

  @doc """
  Returns details about a specific operator module.
  """
  @spec show(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def show(conn, %{"name" => name}) do
    details =
      case name do
        "aggregate_operator" -> %{description: "Aggregates results from multiple child operators."}
        "branch_operator" -> %{description: "Executes conditional branches based on input."}
        "llm_operator" -> %{description: "Runs a language model with a given prompt."}
        "map_operator" -> %{description: "Applies a function to each input item."}
        "parallel_operator" -> %{description: "Runs operators in parallel and merges results."}
        "sequence_operator" -> %{description: "Executes operators sequentially, passing outputs."}
        _ -> %{error: "Operator not found"}
      end
    json(conn, Map.put(details, :name, name))
  end
end
