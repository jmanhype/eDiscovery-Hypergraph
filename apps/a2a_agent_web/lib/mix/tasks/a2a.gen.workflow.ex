defmodule Mix.Tasks.A2a.Gen.Workflow do
  @moduledoc """
  Mix task to generate a new workflow YAML file with a starter template.
  Usage:
      mix a2a.gen.workflow <workflow_name>
  This will create: workflows/<workflow_name>.yaml
  """
  use Mix.Task

  @shortdoc "Generates a new workflow YAML file"

  @impl Mix.Task
  def run([name | _]) when is_binary(name) do
    Mix.shell().info("Generating workflow: #{name}.yaml")
    workflows_dir = Path.expand("../../../workflows", __DIR__)
    File.mkdir_p!(workflows_dir)
    workflow_path = Path.join(workflows_dir, "#{name}.yaml")
    if File.exists?(workflow_path) do
      Mix.shell().error("File already exists: #{workflow_path}")
    else
      File.write!(workflow_path, template(name))
      Mix.shell().info("Created #{workflow_path}")
    end
  end

  def run(_), do: Mix.shell().error("Usage: mix a2a.gen.workflow <workflow_name>")

  @doc """
  Returns a starter YAML workflow template with helpful comments.
  """
  @spec template(String.t()) :: String.t()
  defp template(name) do
    """
# Workflow: #{name}
# Edit the nodes, edges, and parameters as needed.
nodes:
  step1:
    op: MapOperator
    params:
      function: "&(&1 * 2)" # Example: doubles input
  step2:
    op: SequenceOperator
    params:
      steps: [step1]
edges:
  - [step1, step2]
# inputs: {}
# outputs: {}
"""
  end
end
