defmodule A2aAgentWebWeb.AgentRegistryPubSubHandler do
  @moduledoc """
  GenServer to handle distributed agent registry PubSub events.
  Subscribes to the agent_registry topic and delegates messages to AgentRegistry.handle_info/1.
  """
  use GenServer

  @pubsub A2aAgentWeb.PubSub
  @topic "agent_registry"

  @impl true
  def start_link(_opts) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok) do
    Phoenix.PubSub.subscribe(@pubsub, @topic)
    {:ok, %{}}
  end

  @impl true
  def handle_info(msg, state) do
    A2aAgentWebWeb.AgentRegistry.handle_info(msg)
    {:noreply, state}
  end
end
