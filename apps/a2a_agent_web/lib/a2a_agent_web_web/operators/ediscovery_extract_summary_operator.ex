defmodule A2aAgentWebWeb.Operators.EdiscoveryExtractSummaryOperator do
  @moduledoc """
  Extracts the summary from already-processed eDiscovery results.
  """

  require Logger

  @spec call(map()) :: map()
  def call(input) do
    Logger.info("EdiscoveryExtractSummaryOperator received: #{inspect(input)}")
    
    # Extract summary from the processed result
    summary = Map.get(input, "summary", Map.get(input, :summary, "No summary available"))
    
    %{summary: summary}
  end
end