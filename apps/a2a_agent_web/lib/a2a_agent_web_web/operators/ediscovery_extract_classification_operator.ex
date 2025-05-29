defmodule A2aAgentWebWeb.Operators.EdiscoveryExtractClassificationOperator do
  @moduledoc """
  Extracts and transforms classification tags from already-processed eDiscovery results.
  """

  require Logger

  @spec call(map()) :: map()
  def call(input) do
    Logger.info("EdiscoveryExtractClassificationOperator received: #{inspect(input)}")
    
    # Extract tags from the processed result
    tags = Map.get(input, "tags", Map.get(input, :tags, %{}))
    
    # Transform the tags into the expected format
    %{
      privilege_type: if(Map.get(tags, "privileged", false), do: "attorney-client", else: "none"),
      has_evidence: Map.get(tags, "significant_evidence", false),
      evidence_details: nil,
      confidence: 0.95
    }
  end
end