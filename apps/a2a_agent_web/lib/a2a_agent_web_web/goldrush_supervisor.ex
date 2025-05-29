defmodule A2aAgentWebWeb.GoldrushSupervisor do
  @moduledoc """
  Supervisor for event handler processes. Goldrush is a library and cannot be supervised directly.
  Add event handler GenServers here if needed in the future.
  """
  use Supervisor

  def start_link(_init_arg) do
    Supervisor.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok) do
    children = []
    Supervisor.init(children, strategy: :one_for_one)
  end
end
