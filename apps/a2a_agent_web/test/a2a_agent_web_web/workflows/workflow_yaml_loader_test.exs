defmodule A2AAgentWeb.WorkflowYAMELoaderTest do
  @moduledoc """
  Tests for the WorkflowYAMELoader module, ensuring YAML workflows are parsed correctly.
  """
  use ExUnit.Case, async: true

  import A2AAgentWeb.WorkflowYAMELoader

  @yaml_path "workflows/summarize_and_analyze.yaml"

  @doc """
  Test that a valid YAML workflow file is parsed into the expected structure.
  """
  test "loads and parses workflow from YAML" do
    path = Path.join([File.cwd!(), @yaml_path])
    assert {:ok, workflow} = load(path)
    assert %{nodes: nodes, edges: edges} = workflow
    assert Enum.any?(nodes, fn n -> n.id == :summarize and n.op == :LLMOperator end)
    assert Enum.any?(nodes, fn n -> n.id == :analyze and n.op == :MapOperator end)
    assert { :summarize, :analyze } in edges
  end
end
