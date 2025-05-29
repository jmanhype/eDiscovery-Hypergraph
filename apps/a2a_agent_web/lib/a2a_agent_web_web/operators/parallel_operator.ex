defmodule A2aAgentWebWeb.Operators.ParallelOperator do
  @moduledoc """
  Executes multiple operators in parallel and merges their outputs.
  Ember port: ParallelOperator.
  """
  @spec run(any(), [({:fun, (any() -> any())} | {:op, (any() -> any())})]) :: [any()]
  def run(input, ops) when is_list(ops) do
    ops
    |> Enum.map(fn
      {:fun, fun} when is_function(fun, 1) -> fn -> fun.(input) end
      {:op, op} when is_function(op, 1) -> fn -> op.(input) end
      _ -> fn -> input end
    end)
    |> Enum.map(&Task.async/1)
    |> Enum.map(&Task.await/1)
  end
end
