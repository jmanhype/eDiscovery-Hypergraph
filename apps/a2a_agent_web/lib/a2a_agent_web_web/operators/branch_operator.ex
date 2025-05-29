defmodule A2aAgentWebWeb.Operators.BranchOperator do
  @moduledoc """
  Executes one of several branches based on a predicate function.
  Ember port: BranchOperator.

  ## Example
      iex> BranchOperator.run(5, [
      ...>   {fn x -> x > 3 end, fn x -> x * 2 end},
      ...>   {fn x -> true end, fn x -> x - 1 end}
      ...> ])
      10
  """

  @spec run(any(), [{(any() -> boolean()), (any() -> any())}]) :: any()
  def run(input, branches) when is_list(branches) do
    Enum.find_value(branches, fn {pred, op} ->
      if pred.(input), do: op.(input), else: nil
    end)
  end
end
