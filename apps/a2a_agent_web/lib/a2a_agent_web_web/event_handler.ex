defmodule A2aAgentWebWeb.EventHandler do
  @moduledoc """
  Goldrush event handler for A2A agent events.
  Handles message_received, task_started, and error_occurred events.
  """

  require Logger

  @doc """
  Handle a Goldrush event.
  """
  @spec handle_event(atom, map) :: :ok
  def handle_event(:message_received, %{type: type, agent_id: agent_id}) do
    Logger.info("Goldrush: Message received of type #{inspect(type)} from agent #{inspect(agent_id)}")
    :ok
  end

  def handle_event(:task_started, %{task_id: task_id, agent_id: agent_id}) do
    Logger.info("Goldrush: Task started #{inspect(task_id)} by agent #{inspect(agent_id)}")
    :ok
  end

  def handle_event(:error_occurred, %{error: error, agent_id: agent_id}) do
    Logger.error("Goldrush: Error occurred for agent #{inspect(agent_id)}: #{inspect(error)}")
    :ok
  end

  def handle_event(event, payload) do
    Logger.debug("Goldrush: Unhandled event #{inspect(event)} with payload #{inspect(payload)}")
    :ok
  end
end
