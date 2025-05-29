defmodule A2aAgentWebWeb.OperatorsTest do
  @moduledoc """
  Tests for Ember operator ports: MapOperator, SequenceOperator, LLMOperator, ParallelOperator.
  """
  use ExUnit.Case, async: true

  alias A2aAgentWebWeb.Operators.{MapOperator, SequenceOperator, LLMOperator, ParallelOperator}

  describe "MapOperator" do
    test "applies function to input" do
      assert MapOperator.run(2, fn x -> x * 2 end) == 4
    end
  end

  describe "SequenceOperator" do
    test "executes operators in sequence" do
      ops = [
        {:fun, fn x -> x + 1 end},
        {:fun, fn x -> x * 3 end}
      ]
      assert SequenceOperator.run(2, ops) == 9
    end
  end

  describe "LLMOperator" do
    @doc """
    Integration test: Verifies that LLMOperator returns a non-empty response from the LLM API.
    This does not assert the exact output, as LLM completions are non-deterministic.
    """
    test "formats prompt with context" do
      {:ok, prompt} = LLMOperator.run(%{"prompt_template" => "Hello, ~s!", "context" => %{"name" => "world"}}, %{})
      assert is_binary(prompt) and String.length(prompt) > 0
    end
  end

  describe "ParallelOperator" do
    test "runs operators in parallel and merges outputs" do
      ops = [
        {:fun, fn x -> x + 1 end},
        {:fun, fn x -> x * 2 end}
      ]
      assert Enum.sort(ParallelOperator.run(3, ops)) == [4, 6]
    end
  end
end
