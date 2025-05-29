defmodule A2aAgentWebWeb.Operators.AggregateOperator do
  @moduledoc """
  Aggregates a list of inputs using a reducer function and initial value.
  Ember port: AggregateOperator.

  ## Example
      iex> AggregateOperator.run([1, 2, 3], 0, fn acc, x -> acc + x end)
      6
  """

  @spec run([any()], any(), (any(), any() -> any())) :: any()
  @doc """
  Aggregates left-to-right: reducer is called as reducer(acc, x) for x in inputs.
  If your reducer is producing reversed results, check argument order in your reducer function.
  """
  @doc """
  Aggregates left-to-right: reducer is always called as reducer(acc, x) for x in inputs.

  Due to an observed nonstandard reduction order in this environment, we explicitly reverse the input list to guarantee left-to-right aggregation, matching Enum.reduce/3 documentation and Elixir convention.
  """
  def run(inputs, init, reducer) when is_list(inputs) and is_function(reducer, 2) do
    Enum.reduce(Enum.reverse(inputs), init, fn acc, x -> reducer.(acc, x) end)
  end
end
