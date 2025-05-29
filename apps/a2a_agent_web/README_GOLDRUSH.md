# Goldrush Event System for A2A Agent

This document describes the event-driven architecture and best practices for integrating GoldrushEx, GreEx, and Telemetry in the A2A Agent system.

## Directory Structure

- `lib/a2a_agent_web_web/goldrush_handlers.ex` — Goldrush event handler registration and logic
- `lib/a2a_agent_web_web/controllers/` — Phoenix controllers
- `lib/a2a_agent_web_web/operators/` — Operator logic (Ember port)
- `test/a2a_agent_web_web/controllers/` — Controller and event tests

## Event Handler Registration

All Goldrush event handlers are registered in `GoldrushHandlers` at application startup:

```elixir
defmodule A2aAgentWebWeb.GoldrushHandlers do
  @moduledoc """
  Registers Goldrush event handlers for domain events.
  Emits telemetry and supports plugin extensibility.
  """
  @spec setup_handlers() :: :ok | {:error, term()}
  def setup_handlers do
    GoldrushEx.start()
    GoldrushEx.compile(:message_received_handler,
      GoldrushEx.with(GoldrushEx.eq(:event, :message_received), fn event ->
        :telemetry.execute([:a2a_agent, :message_received], %{count: 1}, %{event: event})
        # Plugin hooks can go here
      end)
    )
    GoldrushEx.compile(:task_started_handler,
      GoldrushEx.with(GoldrushEx.eq(:event, :task_started), fn event ->
        :telemetry.execute([:a2a_agent, :task_started], %{count: 1}, %{event: event})
      end)
    )
    GoldrushEx.compile(:error_occurred_handler,
      GoldrushEx.with(GoldrushEx.eq(:event, :error_occurred), fn event ->
        :telemetry.execute([:a2a_agent, :error_occurred], %{count: 1}, %{event: event})
      end)
    )
    :ok
  end
end
```

## Emitting Events at Domain Boundaries

In controllers, operators, or services, emit events at key business logic boundaries:

```elixir
# Example in controller
event = GreEx.make([event: :message_received, type: req_type, agent_id: agent_id])
GoldrushEx.handle(:message_received_handler, event)
```

## Telemetry in Handlers

Emit telemetry events inside Goldrush handler functions for decoupled observability.

## Plugins

Register plugin logic inside handler setup. Example:

```elixir
# In GoldrushHandlers.setup_handlers
GoldrushEx.register_plugin(MyApp.MyPlugin)
```

## Testing

- Use `ExUnit` and `assert_receive` to test event and telemetry emission.
- See `test/a2a_agent_web_web/controllers/agent_controller_goldrush_test.exs` for an example.

## Configuration

- Use environment variables and config files for event/telemetry/Goldrush settings.

## Documentation

- Keep this README and module docstrings up to date as you add new events or handlers.
