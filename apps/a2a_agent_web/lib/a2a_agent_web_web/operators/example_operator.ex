defmodule A2AAgentWebWeb.Operators.ExampleOperator do
  @moduledoc """
  Operator: ExampleOperator
  Implements the Operator protocol for custom workflow steps.
  """

  @behaviour A2AAgentWebWeb.Operator

  @impl true
  @spec call(map(), map()) :: map()
  def call(input, params) do
    # Implement operator logic here
    %{"result" => input["value"]}
  end
end
