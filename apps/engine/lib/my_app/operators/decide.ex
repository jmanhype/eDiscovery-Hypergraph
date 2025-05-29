defmodule MyApp.Operators.Decide do
  @moduledoc """
  Operator module for making decisions based on sentiment.
  """
  @doc "Decides action based on sentiment and threshold."
  @spec call(map(), map()) :: {:ok, any()} | {:error, any()}
  def call(input, params) do
    sentiment = Map.get(input, :sentiment, :neutral)
    threshold = Map.get(params, :threshold, 0.5)
    action = case sentiment do
      :positive -> if threshold < 0.7, do: "Proceed", else: "Hold"
      :negative -> "Review"
      _ -> "Unknown"
    end
    {:ok, %{action: action}}
  end
end
