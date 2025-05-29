defmodule A2aAgentWebWeb.Operators.AggregateOperatorTest do
  @moduledoc """
  Tests for Ember AggregateOperator port.
  Ensures correct aggregation of input lists.
  """
  use ExUnit.Case, async: true

  alias A2aAgentWebWeb.Operators.AggregateOperator

  describe "run/3" do
    test "sums a list of integers" do
      assert AggregateOperator.run([1, 2, 3], 0, fn acc, x -> acc + x end) == 6
    end

    test "concatenates a list of strings" do
      assert AggregateOperator.run(["a", "b", "c"], "", fn acc, x -> acc <> x end) == "abc"
    end

    test "works with empty list and initial value" do
      assert AggregateOperator.run([], 42, fn acc, _x -> acc end) == 42
    end
  end
end
