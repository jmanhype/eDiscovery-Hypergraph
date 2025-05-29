defmodule A2aAgentWebWeb.GoldrushLoggingPlugin do
  @moduledoc """
  Example Goldrush plugin that logs all events processed by GoldrushEx.
  Extend this module for custom plugin logic (e.g., notifications, analytics).

  Note: Plugin registration is not available in this GoldrushEx version, but this module is ready for future compatibility.
  """

  @behaviour GoldrushEx.Plugin

  @impl true
  @spec init(any()) :: {:ok, any()}
  def init(opts), do: {:ok, opts}

  @impl true
  @spec handle_event(any(), any()) :: :ok
  def handle_event(event, _state) do
    require Logger
    Logger.info("[GoldrushPlugin] Event: #{inspect(event)}")
    :ok
  end

  @impl true
  @spec terminate(any(), any()) :: :ok
  def terminate(_reason, _state), do: :ok
end
