defmodule OperatorTest do
  use ExUnit.Case
  doctest Operator

  @moduledoc """
  Tests for Operator protocol and all core operator implementations.
  """

  test "MapOperator.call returns correct output" do
    assert Operator.MapOperator.call(%{"input" => 42}) == %{"output" => 42}
  end

  defmodule TestOpA do
    @behaviour Operator
    def call(input), do: Map.put(input, "a", 1)
  end
  defmodule TestOpB do
    @behaviour Operator
    def call(input), do: Map.put(input, "b", Map.get(input, "a", 0) + 1)
  end
  defmodule TestOpX do
    @behaviour Operator
    def call(_), do: %{"x" => 1}
  end
  defmodule TestOpY do
    @behaviour Operator
    def call(_), do: %{"y" => 2}
  end

  test "SequenceOperator.call chains operators in order" do
    result = Operator.SequenceOperator.call([TestOpA, TestOpB], %{})
    assert result == %{"a" => 1, "b" => 2}
  end

  test "ParallelOperator.call merges outputs from multiple operators" do
    result = Operator.ParallelOperator.call([TestOpX, TestOpY], %{})
    assert result == %{"x" => 1, "y" => 2}
  end

  test "LLMOperator.call returns stubbed LLM response" do
    input = %{"model" => "gpt-4", "prompt" => "Echo: {input}", "input" => "hello"}
    result = Operator.LLMOperator.call(input)
    assert result == %{"response" => "[LLM:gpt-4] Echo: hello"}
  end
end
