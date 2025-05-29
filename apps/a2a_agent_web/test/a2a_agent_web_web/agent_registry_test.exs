defmodule A2aAgentWebWeb.AgentRegistryTest do
  @moduledoc """
  Tests for dynamic AgentRegistry (register, unregister, get, list).
  """
  use ExUnit.Case, async: false
  alias A2aAgentWebWeb.{AgentRegistry, AgentCard}

  setup do
    Agent.update(AgentRegistry, fn _ -> %{} end)
    :ok
  end

  test "registers and lists agents" do
    card = %AgentCard{
      id: "foo",
      name: "Foo",
      version: "1.0",
      description: "Test agent",
      capabilities: ["a"],
      endpoints: %{"a2a" => "/api/a2a"},
      authentication: nil
    }
    assert AgentRegistry.list_agents() == []
    AgentRegistry.register_agent(card)
    assert AgentRegistry.list_agents() == [card]
  end

  test "gets and unregisters agent" do
    card = %AgentCard{id: "bar", name: "Bar", version: "1.0", description: "Bar", capabilities: [], endpoints: %{}, authentication: nil}
    AgentRegistry.register_agent(card)
    assert AgentRegistry.get_agent("bar") == card
    AgentRegistry.unregister_agent("bar")
    assert AgentRegistry.get_agent("bar") == nil
  end
end
