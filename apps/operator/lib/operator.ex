defmodule Operator do
  @moduledoc """
  Operator protocol for composable computation in hypergraph workflows.
  """

  @type t :: module()
  @callback call(map()) :: map()
end

# MapOperator: Applies a function to an input value and returns the result
# Example usage: Operator.MapOperator.call(%{"input" => 42})
defmodule Operator.MapOperator do
  @moduledoc """
  Applies a function to an input value and returns the result.
  """
  @behaviour Operator

  @doc """
  Calls the map operator.
  """
  @impl true
  @spec call(map()) :: map()
  def call(%{"input" => val}) do
    %{"output" => val}
  end
end

# SequenceOperator: Executes a sequence of operators in order
# Example usage: Operator.SequenceOperator.call([op1, op2], input)
defmodule Operator.SequenceOperator do
  @moduledoc """
  Executes a sequence of operators in order, passing outputs from one to the next.
  """

  @doc """
  Calls the sequence of operators.
  """
  @spec call([Operator.t()], map()) :: map()
  def call(operators, input) do
    Enum.reduce(operators, input, fn op, acc -> op.call(acc) end)
  end
end

# ParallelOperator: Executes multiple operators in parallel and merges their outputs
# Example usage: Operator.ParallelOperator.call([op1, op2], input)
defmodule Operator.ParallelOperator do
  @moduledoc """
  Executes multiple operators in parallel and merges their outputs.
  """

  @doc """
  Calls the parallel operators (runs sequentially for now).
  """
  @spec call([Operator.t()], map()) :: map()
  def call(operators, input) do
    operators
    |> Enum.map(fn op -> op.call(input) end)
    |> Enum.reduce(%{}, &Map.merge(&1, &2))
  end
end

# LLMOperator: Executes a language model with a formatted prompt (stub)
defmodule Operator.LLMOperator do
  @moduledoc """
  Executes a language model with a formatted prompt (stub).
  """

  @doc """
  Calls the LLM operator (returns a stubbed response).
  """
  @spec call(map()) :: map()
  def call(%{"model" => model, "prompt" => prompt, "input" => input}) do
    formatted_prompt = String.replace(prompt, "{input}", to_string(input))
    %{"response" => "[LLM:#{model}] #{formatted_prompt}"}
  end
end
