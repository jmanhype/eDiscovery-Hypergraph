defmodule A2aAgentWebWeb.Operators.PassThroughOperator do
  @moduledoc """
  Operator that simply returns its input unchanged.
  Compatible with the orchestrator via call/1.
  """

  @spec call(any()) :: {:ok, any()}
  @doc """
  Orchestrator entrypoint: delegates to run/2.
  """
  def call(input), do: run(input, %{})

  @spec run(any(), any()) :: {:ok, any()}
  @doc """
  Returns the input unchanged, wrapped in {:ok, input}.
  """
  def run(input, _opts), do: {:ok, input}
end
