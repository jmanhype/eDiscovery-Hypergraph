defmodule EngineSpecValidationTest do
  use ExUnit.Case
  doctest Engine

  @moduledoc """
  Tests for Engine graph execution with per-node specification validation.
  """

  defmodule OpEcho do
    @behaviour Operator
    def call(input), do: Map.put(input, "echoed", input["foo"])
  end

  test "node with PassThroughSpecification always passes" do
    graph = %{
      n1: %{operator: OpEcho, deps: [], specification: Operator.PassThroughSpecification}
    }
    result = Engine.run(graph, %{"foo" => 123}, mode: :sequential)
    assert result[:n1]["echoed"] == 123
  end

  test "node with RequiredKeysSpecification passes when key present" do
    graph = %{
      n1: %{operator: OpEcho, deps: [], specification: Operator.RequiredKeysSpecification}
    }
    # RequiredKeysSpecification expects required_keys as second arg, but Engine only calls validate_input/1
    # So this test demonstrates the default impl (which always passes)
    result = Engine.run(graph, %{"foo" => 42}, mode: :sequential)
    assert result[:n1]["echoed"] == 42
  end

  test "node with RequiredKeysSpecification (custom wrapper) fails when key missing" do
    defmodule ReqFooSpec do
      @behaviour Operator.Specification
      def validate_input(input) do
        Operator.RequiredKeysSpecification.validate_input(input, ["foo"])
      end
      def validate_output(_), do: :ok
    end
    graph = %{
      n1: %{operator: OpEcho, deps: [], specification: ReqFooSpec}
    }
    assert_raise RuntimeError, ~r/Input validation failed/, fn ->
      Engine.run(graph, %{"bar" => 1}, mode: :sequential)
    end
  end
end
