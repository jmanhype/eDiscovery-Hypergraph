defmodule Operator.Specification do
  @moduledoc """
  Behaviour for input/output validation and transformation in operator workflows.
  Follows the Specification Pattern for composable, reusable validation logic.
  """

  @callback validate_input(map()) :: :ok | {:error, term()}
  @callback validate_output(map()) :: :ok | {:error, term()}
  @optional_callbacks validate_input: 1, validate_output: 1
end

# Sample: PassThroughSpecification (always passes)
defmodule Operator.PassThroughSpecification do
  @moduledoc """
  A sample specification that always returns :ok for validation.
  """
  @behaviour Operator.Specification
  @impl true
  def validate_input(_input), do: :ok
  @impl true
  def validate_output(_output), do: :ok
end

# Sample: RequiredKeysSpecification (checks required keys in input)
defmodule Operator.RequiredKeysSpecification do
  @moduledoc """
  Validates that required keys are present in the input map.
  """
  @behaviour Operator.Specification
  def validate_input(input, required_keys) when is_list(required_keys) do
    missing = Enum.filter(required_keys, &(!Map.has_key?(input, &1)))
    if missing == [], do: :ok, else: {:error, {:missing_keys, missing}}
  end
  def validate_input(_input), do: :ok
  @impl true
  def validate_output(_output), do: :ok
end
