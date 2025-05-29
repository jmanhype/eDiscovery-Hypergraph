defmodule A2aAgentWebWeb.Operators.EdiscoveryExtractEntitiesOperator do
  @moduledoc """
  Extracts and formats entities from already-processed eDiscovery results.
  """

  require Logger

  @spec call(map()) :: map()
  def call(input) do
    Logger.info("EdiscoveryExtractEntitiesOperator received: #{inspect(input)}")
    
    # Extract entities from the processed result
    entities = Map.get(input, "entities", Map.get(input, :entities, []))
    
    # Format entities consistently
    formatted_entities = Enum.map(entities, fn entity ->
      %{
        name: Map.get(entity, "name", ""),
        type: Map.get(entity, "type", "UNKNOWN"),
        relevance: Map.get(entity, "relevance", "high")
      }
    end)
    
    %{entities: formatted_entities}
  end
end