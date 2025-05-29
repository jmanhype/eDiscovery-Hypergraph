defmodule HypergraphAgent.SampleAgent do
  @moduledoc """
  A sample agent that demonstrates use of before_node/4 and after_node/4 hooks.
  - before_node/4 increments an "a" key in input if present
  - after_node/4 adds a marker to the output
  """

  @spec before_node(any(), map(), module(), map()) :: map()
  def before_node(_node, input, _op, _acc) do
    Map.update(input, "a", 0, &(&1 + 1))
  end

  @spec after_node(any(), map(), module(), map()) :: map()
  def after_node(node, output, _op, _acc) do
    Map.put(output, "agent_marker", "processed_#{node}")
  end
end
