defmodule Mix.Tasks.A2a.Gen.Operator do
  @moduledoc """
  Mix task to scaffold a new Operator module for the A2A Agent system.

  Usage:
      mix a2a.gen.operator MyNewOperator

  This will create: lib/a2a_agent_web_web/operators/my_new_operator.ex
  """
  use Mix.Task

  @shortdoc "Generates a new Operator module"

  @impl Mix.Task
  def run([name | _]) when is_binary(name) do
    module = Macro.camelize(name)
    file = Macro.underscore(name)
    operators_dir = Path.expand("../../../lib/a2a_agent_web_web/operators", __DIR__)
    File.mkdir_p!(operators_dir)
    target = Path.join(operators_dir, "#{file}.ex")
    if File.exists?(target) do
      Mix.shell().error("Operator already exists: #{target}")
    else
      File.write!(target, template(module))
      Mix.shell().info("Created #{target}")
      create_test_file(module, file)
    end
  end

  def run(_), do: Mix.shell().error("Usage: mix a2a.gen.operator <OperatorName>")

  @doc """
  Returns a starter Operator module template.
  """
  @spec template(String.t()) :: String.t()
  defp template(module) do
    """
    defmodule A2AAgentWebWeb.Operators.#{module} do
      @moduledoc \"\"\"
      Operator: #{module}
      Implements the Operator protocol for custom workflow steps.
      \"\"\"
      @behaviour A2AAgentWebWeb.Operator
      @impl true
      @spec call(map(), map()) :: map()
      def call(input, params) do
        # Implement operator logic here
        %{\"result\" => input[\"value\"]}
      end
    end
    """
    |> String.trim_leading()
  end

  @doc """
  Creates a starter test file for the operator, if it does not exist.
  """
  @spec create_test_file(String.t(), String.t()) :: :ok
  defp create_test_file(module, file) do
    test_dir = Path.expand("../../../test/a2a_agent_web_web/operators", __DIR__)
    File.mkdir_p!(test_dir)
    test_file = Path.join(test_dir, "#{file}_test.exs")
    unless File.exists?(test_file) do
      File.write!(test_file, test_template(module))
      Mix.shell().info("Created test #{test_file}")
    end
    :ok
  end

  @doc """
  Returns a starter test template for the operator.
  """
  @spec test_template(String.t()) :: String.t()
  defp test_template(module) do
    """
    defmodule A2AAgentWebWeb.Operators.#{module}Test do
      @moduledoc \"\"\"
      Tests for #{module}.
      \"\"\"
      use ExUnit.Case, async: true

      alias A2AAgentWebWeb.Operators, as: Operators

      @doc \"\"\"
      Ensures #{module}.call/2 returns the expected result.
      \"\"\"
      test "call/2 returns result map" do
        input = %{"value" => 42}
        params = %{}
        assert Operators.#{module}.call(input, params) == %{"result" => 42}
      end
    end
    """
    |> String.trim_leading()
  end
end