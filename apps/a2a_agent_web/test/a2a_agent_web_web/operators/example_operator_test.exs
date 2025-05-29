defmodule A2AAgentWebWeb.Operators.ExampleOperatorTest do
  @moduledoc """
  Tests for ExampleOperator.
  """
  use ExUnit.Case, async: true

  alias A2AAgentWebWeb.Operators.ExampleOperator

  @doc """
  Ensures ExampleOperator.call/2 returns the expected result.
  """
  test "call/2 returns result map" do
    input = %{"value" => 42}
    params = %{}
    assert ExampleOperator.call(input, params) == %{"result" => 42}
  end
end
