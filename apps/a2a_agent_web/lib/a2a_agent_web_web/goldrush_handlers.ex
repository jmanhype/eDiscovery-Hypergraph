defmodule A2aAgentWebWeb.GoldrushHandlers do
  @moduledoc """
  Central registration for Goldrush event handlers in the A2A Agent system.

  ## Event Types
  - `:message_received` — Emitted when an A2A message is received
  - `:task_started` — Emitted when a task or negotiation begins
  - `:error_occurred` — Emitted on orchestration or validation errors

  ## Plugin Extension
  Add plugin logic or registration in this module to extend event processing.
  """
  @moduledoc """
  Goldrush event handlers for A2A agent events.
  Sets up handlers for message_received, task_started, and error_occurred events with telemetry integration.
  """

  @spec setup_handlers() :: :ok | {:error, term()}
  @doc """
  Registers all Goldrush event handlers and emits telemetry for each event type.

  Call this at application startup to ensure handlers are active before processing requests.
  """
  @doc """
  Registers all Goldrush event handlers and emits telemetry for each event type.

  Note: Plugin registration is not available in this GoldrushEx version. To add plugin support, update GoldrushEx and use the appropriate registration API when available.

  Call this at application startup to ensure handlers are active before processing requests.
  """
  def setup_handlers do
    GoldrushEx.start()
    # Plugin registration is not supported in this GoldrushEx version.

    # Message received handler
    msg_query = GoldrushEx.with(GoldrushEx.eq(:event, :message_received), fn event ->
      :telemetry.execute([:a2a_agent, :message_received], %{count: 1}, %{event: event})
      IO.inspect(event, label: "Goldrush: Message Received")
    end)
    GoldrushEx.compile(:message_received_handler, msg_query)

    # Task started handler
    task_query = GoldrushEx.with(GoldrushEx.eq(:event, :task_started), fn event ->
      :telemetry.execute([:a2a_agent, :task_started], %{count: 1}, %{event: event})
      IO.inspect(event, label: "Goldrush: Task Started")
    end)
    GoldrushEx.compile(:task_started_handler, task_query)

    # Error occurred handler
    error_query = GoldrushEx.with(GoldrushEx.eq(:event, :error_occurred), fn event ->
      :telemetry.execute([:a2a_agent, :error_occurred], %{count: 1}, %{event: event})
      IO.inspect(event, label: "Goldrush: Error Occurred")
    end)
    GoldrushEx.compile(:error_occurred_handler, error_query)

    :ok
  end
end
