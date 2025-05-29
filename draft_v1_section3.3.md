# Hypergraph Agents Umbrella: A Multi-Language, High-Performance Agentic AI Framework

## 3. Key Features

### 3.3 Operator System

The Operator System forms the computational building blocks of Hypergraph Agents. Operators encapsulate specific functionality in a consistent interface, enabling developers to compose complex behaviors from simple, reusable components.

#### Built-in Operators

Hypergraph Agents includes several built-in operators to cover common use cases:

1. **MapOperator**: Applies a function to an input value and returns the result.

```elixir
defmodule Operator.MapOperator do
  @moduledoc """
  Applies a function to an input value and returns the result.
  """
  @behaviour Operator

  @impl true
  @spec call(map()) :: map()
  def call(%{"input" => val}) do
    %{"output" => val}
  end
end
```

2. **SequenceOperator**: Executes a sequence of operators in order, passing outputs from one to the next.

```elixir
defmodule Operator.SequenceOperator do
  @moduledoc """
  Executes a sequence of operators in order, passing outputs from one to the next.
  """

  @spec call([Operator.t()], map()) :: map()
  def call(operators, input) do
    Enum.reduce(operators, input, fn op, acc -> op.call(acc) end)
  end
end
```

3. **ParallelOperator**: Executes multiple operators simultaneously and merges their outputs.

```elixir
defmodule Operator.ParallelOperator do
  @moduledoc """
  Executes multiple operators in parallel and merges their outputs.
  """

  @spec call([Operator.t()], map()) :: map()
  def call(operators, input) do
    operators
    |> Enum.map(fn op -> op.call(input) end)
    |> Enum.reduce(%{}, &Map.merge(&1, &2))
  end
end
```

4. **LLMOperator**: Interfaces with language models to generate text based on prompts.

```elixir
defmodule Operator.LLMOperator do
  @moduledoc """
  Executes a language model with a formatted prompt.
  """

  @spec call(map()) :: map()
  def call(%{"model" => model, "prompt" => prompt, "input" => input}) do
    formatted_prompt = String.replace(prompt, "{input}", to_string(input))
    %{"response" => "[LLM:#{model}] #{formatted_prompt}"}
  end
end
```

These operators provide a foundation for building more complex workflows while adhering to a consistent interface.

#### Custom Operator Development

The system is designed for easy extension with custom operators. Developers can create new operators by implementing the `Operator` behavior:

```elixir
defmodule MyCustomOperator do
  @moduledoc """
  Custom operator for specific business logic.
  """
  @behaviour Operator

  @impl true
  @spec call(map()) :: map()
  def call(input) do
    # Custom implementation goes here
    transformed_data = process_data(input["data"])
    %{"result" => transformed_data}
  end

  defp process_data(data) do
    # Processing logic
    String.upcase(data)
  end
end
```

The framework includes tools to generate operator scaffolding:

```sh
mix a2a.gen.operator MyOperator
```

This creates a new operator module with proper structure, tests, and documentation templates.

#### Specification Protocol and Validation

To ensure operators receive and produce compatible data, Hypergraph Agents includes a specification protocol:

```elixir
defmodule Operator.Specification do
  @callback validate_input(map()) :: :ok | {:error, String.t()}
  @callback validate_output(map()) :: :ok | {:error, String.t()}
end
```

Operators can implement specifications to validate inputs and outputs:

```elixir
defmodule MyOperator.Specification do
  @behaviour Operator.Specification

  @impl true
  def validate_input(input) do
    cond do
      not Map.has_key?(input, "text") ->
        {:error, "Input must contain 'text' key"}
      not is_binary(input["text"]) ->
        {:error, "Input 'text' must be a string"}
      true -> :ok
    end
  end

  @impl true
  def validate_output(output) do
    cond do
      not Map.has_key?(output, "result") ->
        {:error, "Output must contain 'result' key"}
      true -> :ok
    end
  end
end
```

The workflow engine automatically applies these validations during execution, ensuring type safety and proper data flow between operators.

#### Composable Computation

The true power of operators lies in their composability. Complex workflows can be constructed by combining simple operators:

```elixir
workflow = %{
  "extract" => %{
    operator: TextExtractOperator,
    deps: []
  },
  "analyze" => %{
    operator: SentimentOperator,
    deps: ["extract"]
  },
  "summarize" => %{
    operator: LLMOperator,
    params: %{
      model: "gpt-4",
      prompt: "Summarize this text: {input}"
    },
    deps: ["extract"]
  },
  "combine" => %{
    operator: CombineOperator,
    deps: ["analyze", "summarize"]
  }
}

Engine.run(workflow, %{"document" => "path/to/document.pdf"})
```

This compositional approach enables developers to build sophisticated workflows from small, testable components, enhancing code reuse and maintainability while reducing complexity. 