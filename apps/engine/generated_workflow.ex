defmodule GeneratedWorkflow do
  @moduledoc "Auto-generated workflow module."

  @doc "Node step1 executes operation :summarize with params %{prompt: 'Summarize this text.'}."
  @spec step1(map()) :: {:ok, any()}
  def step1(input) do
    # Calls the operator module's call/2 function
    operator = Module.concat([MyApp, Operators, Summarize])
    case operator.call(input, %{prompt: "Summarize this text."}) do
      {:ok, result} -> {:ok, result}
      {:error, reason} -> raise "Operator summarize failed: #{inspect(reason)}"
      other -> {:ok, other}
    end
  end


  @doc "Node step2 executes operation :analyze_sentiment with params %{}."
  @spec step2(map()) :: {:ok, any()}
  def step2(input) do
    # Calls the operator module's call/2 function
    operator = Module.concat([MyApp, Operators, AnalyzeSentiment])
    case operator.call(input, %{}) do
      {:ok, result} -> {:ok, result}
      {:error, reason} -> raise "Operator analyze_sentiment failed: #{inspect(reason)}"
      other -> {:ok, other}
    end
  end


  @doc "Node step3 executes operation :decide with params %{threshold: 0.5}."
  @spec step3(map()) :: {:ok, any()}
  def step3(input) do
    # Calls the operator module's call/2 function
    operator = Module.concat([MyApp, Operators, Decide])
    case operator.call(input, %{threshold: 0.5}) do
      {:ok, result} -> {:ok, result}
      {:error, reason} -> raise "Operator decide failed: #{inspect(reason)}"
      other -> {:ok, other}
    end
  end


  def run(input) do
    { :ok, step1_out } = step1(input)
    { :ok, step2_out } = step2(input)
    { :ok, step3_out } = step3(input)
  end
end
