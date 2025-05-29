defmodule A2aAgentWebWeb.A2AMessageTest do
  use ExUnit.Case, async: true
  alias A2aAgentWebWeb.A2AMessage

  describe "validate/1" do
    test "valid message" do
      params = %{"type" => "task_request", "sender" => "agent1", "recipient" => "agent2", "payload" => %{}}
      assert {:ok, %A2AMessage{type: :task_request, sender: "agent1", recipient: "agent2", payload: %{}}} = A2AMessage.validate(params)
    end

    test "missing required fields" do
      params = %{"type" => "task_request", "sender" => "agent1"}
      assert {:error, msg} = A2AMessage.validate(params)
      assert msg =~ "Missing required fields"
    end

    test "invalid type" do
      params = %{"type" => "not_a_type", "sender" => "a", "recipient" => "b", "payload" => %{}}
      assert {:error, msg} = A2AMessage.validate(params)
      assert msg =~ "Invalid type"
    end
  end
end
