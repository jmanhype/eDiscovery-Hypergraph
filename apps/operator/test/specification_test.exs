defmodule SpecificationTest do
  use ExUnit.Case
  doctest Operator.Specification

  @moduledoc """
  Tests for the Operator.Specification behaviour and sample implementations.
  """

  test "PassThroughSpecification always passes validation" do
    assert Operator.PassThroughSpecification.validate_input(%{"foo" => 1}) == :ok
    assert Operator.PassThroughSpecification.validate_output(%{"bar" => 2}) == :ok
  end

  test "RequiredKeysSpecification validates required keys" do
    input = %{"a" => 1, "b" => 2}
    assert Operator.RequiredKeysSpecification.validate_input(input, ["a"]) == :ok
    assert Operator.RequiredKeysSpecification.validate_input(input, ["a", "b"]) == :ok
    assert Operator.RequiredKeysSpecification.validate_input(input, ["a", "b", "c"]) == {:error, {:missing_keys, ["c"]}}
    assert Operator.RequiredKeysSpecification.validate_input(%{}, ["x"]) == {:error, {:missing_keys, ["x"]}}
  end
end
