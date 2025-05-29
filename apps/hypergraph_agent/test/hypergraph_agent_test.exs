defmodule HypergraphAgentTest do
  use ExUnit.Case
  doctest HypergraphAgent

  @moduledoc """
  Tests for the HypergraphAgent protocol and BasicAgent implementation.
  """

  test "BasicAgent.act adds :acted key" do
    input = %{foo: "bar"}
    result = HypergraphAgent.BasicAgent.act(input)
    assert result[:acted] == true
    assert result[:foo] == "bar"
  end

end
