defmodule A2aAgentWebWeb.Operators.EdiscoveryClassificationOperator do
  @moduledoc """
  Operator for classifying legal documents for privilege and evidence significance.
  """

  # alias A2aAgentWebWeb.EventBus # TODO: Enable when EventBus supports request/reply
  require Logger

  @spec run(any(), map()) :: {:ok, map()} | {:error, String.t()}
  def run(input, ctx) do
    email_content = get_email_content(input)
    
    # EventBus doesn't support request/reply yet, use HTTP directly
    send_via_http(email_content, ctx)
  end

  defp get_email_content(input) when is_map(input) do
    Map.get(input, "email", Map.get(input, "content", ""))
  end
  defp get_email_content(input) when is_binary(input), do: input

  # TODO: Implement when EventBus supports request/reply pattern
  # defp send_via_nats(content, _ctx) do
  #   request = %{
  #     subject: content,
  #     body: content,
  #     email_id: generate_email_id()
  #   }
  #
  #   case EventBus.request("ediscovery.classify", request, timeout: 10_000) do
  #     {:ok, classification} -> {:ok, parse_classification(classification)}
  #     error -> error
  #   end
  # end

  defp send_via_http(content, _ctx) do
    url = System.get_env("EDISCOVERY_API_URL", "http://localhost:8001/api/ediscovery/process")
    
    body = Jason.encode!(%{
      emails: [
        %{
          subject: "Legal Classification Request",
          body: content
        }
      ]
    })

    case HTTPoison.post(url, body, [{"Content-Type", "application/json"}], timeout: 60_000, recv_timeout: 60_000) do
      {:ok, %{status_code: 200, body: resp_body}} ->
        case Jason.decode(resp_body) do
          {:ok, %{"results" => [result | _]}} -> 
            tags = Map.get(result, "tags", %{})
            {:ok, %{
              privilege_type: (if Map.get(tags, "privileged"), do: "attorney-client", else: "none"),
              has_evidence: Map.get(tags, "significant_evidence", false),
              evidence_details: nil,
              confidence: 0.8
            }}
          _ -> 
            {:error, "Invalid response format"}
        end
      
      error ->
        Logger.error("HTTP request failed: #{inspect(error)}")
        {:error, "Failed to classify document"}
    end
  end

  # No longer needed with the new API format
  # defp parse_classification(classification) when is_map(classification) do
  #   %{
  #     privilege_type: Map.get(classification, "privilege_type"),
  #     has_evidence: Map.get(classification, "has_evidence", false),
  #     evidence_details: Map.get(classification, "evidence_details"),
  #     confidence: Map.get(classification, "confidence", 0.0)
  #   }
  # end
  # 
  # defp parse_classification(_), do: %{privilege_type: nil, has_evidence: false}

  # TODO: Uncomment when EventBus supports request/reply
  # defp generate_email_id do
  #   "email_#{:os.system_time(:millisecond)}_#{:rand.uniform(1000)}"
  # end

  @doc """
  Workflow engine compatibility - delegates to run/2 with empty context
  """
  @spec call(map()) :: map()
  def call(params) do
    case run(params, %{}) do
      {:ok, result} -> result
      {:error, reason} -> %{error: reason}
    end
  end
end