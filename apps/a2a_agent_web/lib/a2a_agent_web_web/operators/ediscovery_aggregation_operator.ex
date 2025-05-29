defmodule A2aAgentWebWeb.Operators.EdiscoveryAggregationOperator do
  @moduledoc """
  Aggregates results from the three eDiscovery operators into a single result.
  """

  @spec call(map()) :: map()
  def call(input) do
    # The workflow engine merges all dependency results into a single map
    # Extract the relevant fields from the merged input
    %{
      summary: Map.get(input, :summary, Map.get(input, "summary", "")),
      classification: %{
        privilege_type: Map.get(input, :privilege_type, Map.get(input, "privilege_type", "none")),
        has_evidence: Map.get(input, :has_evidence, Map.get(input, "has_evidence", false)),
        evidence_details: Map.get(input, :evidence_details, Map.get(input, "evidence_details")),
        confidence: Map.get(input, :confidence, Map.get(input, "confidence", 0.0))
      },
      entities: Map.get(input, :entities, Map.get(input, "entities", [])),
      processed_at: DateTime.utc_now() |> DateTime.to_iso8601()
    }
  end
end