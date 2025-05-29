defmodule A2aAgentWebWeb.AgentRegistry do
  @moduledoc """
  Distributed in-memory registry for agent discovery and dynamic registration.
  Uses Phoenix.PubSub to sync agent cards across nodes.
  Stores AgentCard structs for each registered agent.
  """

  use Agent
  alias A2aAgentWebWeb.AgentCard
  require Logger

  @pubsub A2aAgentWeb.PubSub
  @topic "agent_registry"

  @persist_path Application.compile_env(:a2a_agent_web, :agent_registry_persist_path, "tmp/agent_registry_state.bin")

  @doc """
  Starts the AgentRegistry process, loads state from disk, and subscribes to PubSub events.
  """
  @spec start_link(any()) :: {:ok, pid()} | {:error, any()}
  def start_link(_opts) do
    state = load_state()
    res = Agent.start_link(fn -> state end, name: __MODULE__)
    Phoenix.PubSub.subscribe(@pubsub, @topic)
    # On startup, request sync from other nodes
    Phoenix.PubSub.broadcast(@pubsub, @topic, {:sync_request, node()})
    res
  end

  @doc """
  Loads registry state from disk, or returns empty map if not found or error.
  """
  @spec load_state() :: map()
  defp load_state do
    case File.read(@persist_path) do
      {:ok, bin} ->
        try do
          :erlang.binary_to_term(bin)
        rescue
          _ -> %{}
        end
      _ -> %{}
    end
  end

  @doc """
  Persists registry state to disk.
  """
  @spec persist_state(map()) :: :ok | {:error, any()}
  defp persist_state(state) do
    File.mkdir_p!(Path.dirname(@persist_path))
    bin = :erlang.term_to_binary(state)
    File.write(@persist_path, bin)
  end

  @doc """
  Registers an agent by AgentCard struct. Overwrites if id already exists.
  Broadcasts to all nodes.
  """
  @spec register_agent(AgentCard.t()) :: :ok
  def register_agent(%AgentCard{id: id} = card) do
    Agent.update(__MODULE__, fn state ->
      new = Map.put(state, id, card)
      persist_state(new)
      new
    end)
    Phoenix.PubSub.broadcast(@pubsub, @topic, {:register_agent, card, node()})
    :ok
  end

  @doc """
  Unregisters an agent by id. Broadcasts to all nodes.
  """
  @spec unregister_agent(String.t()) :: :ok
  def unregister_agent(id) when is_binary(id) do
    Agent.update(__MODULE__, fn state ->
      new = Map.delete(state, id)
      persist_state(new)
      new
    end)
    Phoenix.PubSub.broadcast(@pubsub, @topic, {:unregister_agent, id, node()})
    :ok
  end

  @doc """
  Gets an agent by id. Returns nil if not found.
  """
  @spec get_agent(String.t()) :: AgentCard.t() | nil
  def get_agent(id) when is_binary(id) do
    Agent.get(__MODULE__, &Map.get(&1, id))
  end

  @doc """
  Returns a list of all registered AgentCards.
  """
  @spec list_agents() :: [AgentCard.t()]
  def list_agents do
    Agent.get(__MODULE__, &Map.values(&1))
  end

  @doc """
  Handles incoming PubSub messages for distributed registry sync.
  Should be called from your app's endpoint or supervisor.
  """
  @spec handle_info(term(), boolean()) :: :ok
  def handle_info(msg, do_broadcast? \\ false)

  def handle_info({:register_agent, %AgentCard{id: id} = card, from_node}, do_broadcast?) do
    if from_node != node() do
      Agent.update(__MODULE__, fn state ->
        new = Map.put(state, id, card)
        persist_state(new)
        new
      end)
      if do_broadcast?, do: Phoenix.PubSub.broadcast(@pubsub, @topic, {:register_agent, card, node()})
    end
    :ok
  end

  def handle_info({:unregister_agent, id, from_node}, do_broadcast?) do
    if from_node != node() do
      Agent.update(__MODULE__, fn state ->
        new = Map.delete(state, id)
        persist_state(new)
        new
      end)
      if do_broadcast?, do: Phoenix.PubSub.broadcast(@pubsub, @topic, {:unregister_agent, id, node()})
    end
    :ok
  end

  def handle_info({:sync_request, requester_node}, _do_broadcast?) do
    if requester_node != node() do
      # Send full registry state to requester node
      state = Agent.get(__MODULE__, & &1)
      Phoenix.PubSub.broadcast(@pubsub, @topic, {:sync_response, state, node(), requester_node})
    end
    :ok
  end

  def handle_info({:sync_response, remote_state, from_node, to_node}, _do_broadcast?) do
    if to_node == node() and from_node != node() do
      # Merge remote state into local registry
      Agent.update(__MODULE__, fn local ->
        merged = Map.merge(local, remote_state)
        persist_state(merged)
        merged
      end)
    end
    :ok
  end

  def handle_info(_msg, _), do: :ok
end
