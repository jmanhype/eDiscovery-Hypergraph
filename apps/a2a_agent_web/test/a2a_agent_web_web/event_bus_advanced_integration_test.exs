"""
Integration tests for advanced NATS event bus scenarios:
- Multiple subscribers
- Large payloads
- Error handling (malformed event)
"""

defmodule A2aAgentWebWeb.EventBusAdvancedIntegrationTest do
  use ExUnit.Case, async: false

  @moduletag :integration

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

  @doc """
  Multiple subscribers receive the same event.
  """
  test "multiple subscribers receive the same event" do
    wait_for_nats_conn()
    subject = "a2a.events.test.multiple." <> Integer.to_string(System.unique_integer([:positive]))
    event = %{foo: "multi", value: 42}

    # Spawn two subscribers
    parent = self()
    sub1 = spawn(fn ->
      Gnat.sub(:a2a_nats, self(), subject)
      send(parent, {:ready, :sub1})
      assert_receive {:msg, %{body: body}}, 1000
      send(parent, {:sub1, Jason.decode!(body)})
    end)
    sub2 = spawn(fn ->
      Gnat.sub(:a2a_nats, self(), subject)
      send(parent, {:ready, :sub2})
      assert_receive {:msg, %{body: body}}, 1000
      send(parent, {:sub2, Jason.decode!(body)})
    end)
    # Wait for both to subscribe
    assert_receive {:ready, :sub1}
    assert_receive {:ready, :sub2}

    # Publish the event
    :ok = A2aAgentWebWeb.EventBus.publish(event, subject)

    # Both subscribers should receive the event
    assert_receive {:sub1, %{"foo" => "multi", "value" => 42}}
    assert_receive {:sub2, %{"foo" => "multi", "value" => 42}}
  end

  @doc """
  Large payloads are delivered correctly.
  """
  test "large payload is delivered" do
    wait_for_nats_conn()
    subject = "a2a.events.test.large." <> Integer.to_string(System.unique_integer([:positive]))
    payload = String.duplicate("x", 100_000)
    event = %{blob: payload}

    Gnat.sub(:a2a_nats, self(), subject)
    :ok = A2aAgentWebWeb.EventBus.publish(event, subject)
    assert_receive {:msg, %{body: body}}, 1000
    assert Jason.decode!(body)["blob"] == payload
  end

  @doc """
  Malformed event does not crash the subscriber.
  """
  test "malformed event is handled gracefully" do
    wait_for_nats_conn()
    subject = "a2a.events.test.malformed." <> Integer.to_string(System.unique_integer([:positive]))

    Gnat.sub(:a2a_nats, self(), subject)
    # Publish a non-JSON payload
    :ok = Gnat.pub(:a2a_nats, subject, "not a json!")
    # Should log a warning but not crash
    assert_receive {:msg, %{body: "not a json!"}}, 1000
  end
end
