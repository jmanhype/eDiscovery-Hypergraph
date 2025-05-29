defmodule A2AAgentWebWeb.Operators.MyOperatorTest do
  @moduledoc """
  Tests for MyOperator.
  """
  use ExUnit.Case, async: true

  alias A2AAgentWebWeb.Operators, as: Operators

  @doc """
  Ensures MyOperator.call/2 returns the expected result.
  """
  test "call/2 returns result map" do
    input = %{"value" => 42}
    params = %{}
    assert Operators.MyOperator.call(input, params) == %{"result" => 42}
  end
end
