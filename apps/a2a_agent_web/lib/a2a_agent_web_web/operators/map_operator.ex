defmodule A2aAgentWebWeb.Operators.MapOperator do
  @moduledoc """
  Applies a function to an input value and returns the result.
  Ember port: MapOperator.
  """

  @spec run(any(), (any() -> any())) :: any()
  def run(input, fun) when is_function(fun, 1) do
    fun.(input)
  end

  @doc """
  Pass-through operator for workflow engine compatibility. Returns params unchanged.
  """
  @spec call(map()) :: map()
  def call(params), do: params
end
