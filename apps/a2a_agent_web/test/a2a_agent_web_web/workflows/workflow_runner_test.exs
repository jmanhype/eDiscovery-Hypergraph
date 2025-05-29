defmodule A2AAgentWeb.WorkflowRunnerTest do
  @moduledoc """
  Tests for the WorkflowRunner module, ensuring workflows can be loaded and executed end-to-end.
  """
  use ExUnit.Case, async: true

  alias A2AAgentWeb.WorkflowRunner

  @yaml_path "workflows/summarize_and_analyze.yaml"
  @exs_path "workflows/summarize_and_analyze.exs"

  @doc """
  Test running a workflow from YAML through the runner (mocking Engine.run/2).
  """
  test "run_yaml executes the workflow" do
    defmodule EngineMock do
      def run(workflow, input) do
        assert is_map(workflow)
        assert Map.has_key?(workflow, :nodes)
        assert Map.has_key?(workflow, :edges)
        {:ok, :yaml, workflow, input}
      end
    end
    path = Path.join([File.cwd!(), @yaml_path])
    assert {:ok, :yaml, workflow, input} = WorkflowRunner.run_yaml(path, %{text: "Elixir YAML"}, EngineMock)
    assert input[:text] == "Elixir YAML"
  end

  # Macro DSL test is commented out until builder pattern refactor is complete
  # @doc """
  # Test running a workflow from Elixir macro DSL through the runner (mocking Engine.run/2).
  # """
  # test "run_exs executes the workflow" do
  #   defmodule Engine do
  #     def run(workflow, input), do: {:ok, :exs, workflow, input}
  #   end
  #   path = Path.join([File.cwd!(), @exs_path])
  #   assert {:ok, :exs, workflow, input} = WorkflowRunner.run_exs(path, %{text: "Elixir Macro"})
  #   assert %{nodes: nodes, edges: edges} = workflow
  #   assert input[:text] == "Elixir Macro"
  # end

end
