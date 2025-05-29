defmodule A2aAgentWebWeb.Operators.SequenceOperator do
  @moduledoc """
  Executes a sequence of operators in order, passing outputs from one to the next.
  Ember port: SequenceOperator.
  """

  @spec run(any(), [({:fun, (any() -> any())} | {:op, (any() -> any())})]) :: any()
  def run(input, ops) when is_list(ops) do
    Enum.reduce(ops, input, fn
      {:fun, fun}, acc when is_function(fun, 1) -> fun.(acc)
      {:op, op}, acc when is_function(op, 1) -> op.(acc)
      _, acc -> acc
    end)
  end
end
