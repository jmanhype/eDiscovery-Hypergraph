"""
Integration tests for the A2aAgentWebWeb.EventBus module.
Ensures real publish/subscribe over a running NATS server.
"""

Application.ensure_all_started(:a2a_agent_web)

defmodule A2aAgentWebWeb.EventBusIntegrationTest do
  use ExUnit.Case, async: false

  @moduletag :integration

  @doc """
  Publishes an event and verifies it is received via NATS.
  Requires a running NATS server on localhost:4222.
  """
  setup_all do
    # Try to start EventBus, but handle if already started
    case start_supervised(A2aAgentWebWeb.EventBus) do
      {:ok, _pid} -> :ok
      {:error, {:already_started, _pid}} -> :ok
      other -> raise "Could not start EventBus: #{inspect(other)}"
    end
  end

  defp wait_for_nats_conn(timeout_ms \\ 2000) do
    start = System.monotonic_time(:millisecond)
    until = start + timeout_ms
    do_wait(until)
  end

  defp do_wait(until) do
    if Process.whereis(:a2a_nats) do
      :ok
    else
      if System.monotonic_time(:millisecond) < until do
        Process.sleep(50)
        do_wait(until)
      else
        flunk("NATS connection (:a2a_nats) did not start in time!")
      end
    end
  end

  test "publishes and receives event via NATS" do
    wait_for_nats_conn()

    subject = "a2a.events.test." <> Integer.to_string(System.unique_integer([:positive]))
    event = %{foo: "bar", test: true}

    # Subscribe to the subject
    {:ok, _sid} = Gnat.sub(:a2a_nats, self(), subject)

    # Publish the event
    :ok = A2aAgentWebWeb.EventBus.publish(event, subject)

    # Assert we receive it within a timeout
    assert_receive {:msg, %{body: body}}, 1000
    assert Jason.decode!(body) == %{"foo" => "bar", "test" => true}
  end
end
