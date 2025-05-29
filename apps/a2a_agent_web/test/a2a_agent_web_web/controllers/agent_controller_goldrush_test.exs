import ExUnit.CaptureLog
import ExUnit.Assertions
import ExUnit.Case

if Code.ensure_loaded?(GoldrushEx) and Code.ensure_loaded?(GreEx) do
  defmodule A2aAgentWebWeb.AgentControllerGoldrushTest do
  @moduledoc """
  Tests GoldrushEx and telemetry event emission for A2A Agent system.

  - Asserts :message_received events and telemetry are emitted for valid messages.
  - Demonstrates best-practice event/telemetry test pattern with assert_receive.
  """
    use A2aAgentWebWeb.ConnCase, async: true

    @moduletag :a2a

    @doc """
    Test that GoldrushEx emits a :message_received event and telemetry when a valid message is posted.
    """
    test "POST valid A2A message emits Goldrush event and telemetry", %{conn: conn} do
      :telemetry.attach(
        "test-goldrush-message-received",
        [:a2a_agent, :message_received],
        fn event, measurements, metadata, _config ->
          send(self(), {:telemetry_event, event, measurements, metadata})
        end,
        nil
      )

      body = %{
        "type" => "task_request",
        "sender" => "agent1",
        "recipient" => "agent2",
        "payload" => %{
          "graph" => %{"nodes" => [], "edges" => []},
          "agent_map" => %{},
          "input" => %{}
        }
      }

      _log = capture_log(fn ->
        post(conn, "/api/a2a", body)
      end)

      assert_receive {:telemetry_event, [:a2a_agent, :message_received], %{count: 1}, %{event: event}}, 1000
      event_list =
        case event do
          {:list, kvs} -> kvs
          kvs when is_list(kvs) -> kvs
          _ -> []
        end
      assert Keyword.get(event_list, :type) in ["task_request", :task_request]
      assert Keyword.get(event_list, :agent_id) == "agent1"

      :telemetry.detach("test-goldrush-message-received")
    end
  end
end
