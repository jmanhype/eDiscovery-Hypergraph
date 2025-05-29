defmodule EngineTest do
  use ExUnit.Case
  doctest Engine

  @moduledoc """
  Tests for the Engine (hypergraph execution engine) module.
  """

  defmodule OpA do
    @behaviour Operator
    def call(input), do: Map.put(input, "a", 1)
  end
  defmodule OpB do
    @behaviour Operator
    def call(input), do: Map.put(input, "b", Map.get(input, "a", 0) + 1)
  end
  defmodule OpC do
    @behaviour Operator
    def call(input), do: Map.put(input, "c", Map.get(input, "a", 0) + Map.get(input, "b", 0))
  end

  test "sequential execution: linear chain" do
    graph = %{
      a: %{operator: OpA, deps: []},
      b: %{operator: OpB, deps: [:a]},
      c: %{operator: OpC, deps: [:a, :b]}
    }
    result = Engine.run(graph, %{}, mode: :sequential)
    assert result[:a] == %{"a" => 1}
    assert result[:b] == %{"a" => 1, "b" => 2}
    assert result[:c] == %{"a" => 1, "b" => 2, "c" => 3}
  end

  test "parallel execution: two independent branches" do
    defmodule OpX do
      @behaviour Operator
      def call(input), do: Map.put(input, "x", 10)
    end
    defmodule OpY do
      @behaviour Operator
      def call(input), do: Map.put(input, "y", 20)
    end
    graph = %{
      x: %{operator: OpX, deps: []},
      y: %{operator: OpY, deps: []}
    }
    result = Engine.run(graph, %{}, mode: :parallel)
    assert result[:x] == %{"x" => 10}
    assert result[:y] == %{"y" => 20}
  end

  test "dependency enforcement: child sees parent output" do
    defmodule Parent do
      @behaviour Operator
      def call(_), do: %{"foo" => 42}
    end
    defmodule Child do
      @behaviour Operator
      def call(input), do: Map.put(input, "bar", input["foo"] + 1)
    end
    graph = %{
      parent: %{operator: Parent, deps: []},
      child: %{operator: Child, deps: [:parent]}
    }
    result = Engine.run(graph, %{}, mode: :sequential)
    assert result[:parent] == %{"foo" => 42}
    assert result[:child] == %{"foo" => 42, "bar" => 43}
  end
end
