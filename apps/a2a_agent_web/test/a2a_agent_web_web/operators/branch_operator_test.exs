defmodule A2aAgentWebWeb.Operators.BranchOperatorTest do
  @moduledoc """
  Tests for Ember BranchOperator port.
  Ensures correct branch is executed based on predicate.
  """
  use ExUnit.Case, async: true

  alias A2aAgentWebWeb.Operators.BranchOperator

  describe "run/2" do
    test "executes first matching branch" do
      branches = [
        {fn x -> x > 3 end, fn x -> x * 2 end},
        {fn x -> true end, fn x -> x - 1 end}
      ]
      assert BranchOperator.run(5, branches) == 10
      assert BranchOperator.run(2, branches) == 1
    end

    test "returns nil if no branch matches" do
      branches = [
        {fn x -> false end, fn x -> x * 2 end}
      ]
      assert BranchOperator.run(1, branches) == nil
    end
  end
end
