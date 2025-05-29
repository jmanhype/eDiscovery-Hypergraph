defmodule MyApp.Operators.AnalyzeSentiment do
  @moduledoc """
  Operator module for sentiment analysis.
  """
  @doc "Analyzes sentiment of the summary. Returns :positive or :negative."
  @spec call(map(), map()) :: {:ok, any()} | {:error, any()}
  def call(input, _params) do
    summary = Map.get(input, :summary, "")
    sentiment = if String.contains?(summary, "good"), do: :positive, else: :negative
    {:ok, %{sentiment: sentiment}}
  end
end
