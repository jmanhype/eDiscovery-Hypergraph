defmodule A2AAgentWeb.WorkflowRunner do
  @moduledoc """
  Loads a workflow (YAML or Elixir macro DSL) and executes it using the XCS engine.

  - Use `run_yaml/2` to load and run a YAML workflow.
  - Use `run_exs/2` to load and run an Elixir macro DSL workflow.

  Example:
      A2AAgentWeb.WorkflowRunner.run_yaml("workflows/summarize_and_analyze.yaml", %{"text" => "Elixir is awesome!"})
      A2AAgentWeb.WorkflowRunner.run_exs("workflows/summarize_and_analyze.exs", %{"text" => "Elixir is awesome!"})
  """

  alias A2AAgentWeb.WorkflowYAMELoader
  # For Elixir macro DSL, no alias needed; Code.eval_file/1 returns the workflow structure

  @doc """
  Loads a workflow from YAML and executes it with the XCS engine.

  Always passes the full workflow map (with :nodes and :edges) to the engine. Optional engine module for testability.

  ## Parameters
    - yaml_path: Path to the YAML workflow file
    - input: Input map for the workflow
    - engine: (optional) Engine module (defaults to Engine)

  ## Returns
    - The result of engine.run/2
  """
  @spec run_yaml(String.t(), map(), module()) :: any()
  def run_yaml(yaml_path, input \\ %{}, engine \\ Engine) do
    case WorkflowYAMELoader.load(yaml_path) do
      {:ok, %{:nodes => _nodes, :edges => _edges} = workflow} ->
        engine.run(workflow, input)
      {:ok, %{"nodes" => _nodes, "edges" => _edges} = workflow} ->
        # Convert string keys to atoms for engine compatibility
        atomized = %{
          nodes: Enum.map(workflow["nodes"], &string_key_to_atom_map/1),
          edges: Enum.map(workflow["edges"], &string_edge_to_tuple/1)
        }
        engine.run(atomized, input)
      {:error, err} ->
        {:error, err}
      other ->
        {:error, {:unexpected_workflow_structure, other}}
    end
  end

  @doc false
  @spec string_key_to_atom_map(map()) :: map()
  defp string_key_to_atom_map(map) when is_map(map) do
    map
    |> Enum.map(fn {k, v} -> {String.to_atom(to_string(k)), atomize_value(v)} end)
    |> Enum.into(%{})
  end

  defp atomize_value(v) when is_map(v), do: string_key_to_atom_map(v)
  defp atomize_value(v) when is_list(v), do: Enum.map(v, &atomize_value/1)
  defp atomize_value(v) when is_binary(v) do
    # Try to convert to atom if possible for known fields (like op, id, depends_on)
    if String.match?(v, ~r/^\w+$/) do
      String.to_atom(v)
    else
      v
    end
  end
  defp atomize_value(v), do: v


  @doc false
  @spec string_edge_to_tuple(String.t() | tuple()) :: tuple()
  defp string_edge_to_tuple(edge) when is_tuple(edge), do: edge
  defp string_edge_to_tuple(edge) when is_binary(edge) do
    [from, to] = String.split(edge, "->")
    {String.to_atom(from), String.to_atom(to)}
  end

  @doc """
  Loads a workflow from an Elixir macro DSL file and executes it with the XCS engine. Optional engine module for testability.
  """
  @spec run_exs(String.t(), map(), module()) :: any()
  def run_exs(exs_path, input \\ %{}, engine \\ Engine) do
    {workflow, _binding} = Code.eval_file(exs_path)
    engine.run(workflow, input)
  end
end
