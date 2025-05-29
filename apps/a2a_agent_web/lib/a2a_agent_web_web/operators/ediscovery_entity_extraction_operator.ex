defmodule A2aAgentWebWeb.Operators.EdiscoveryEntityExtractionOperator do
  @moduledoc """
  Operator for extracting entities (people, organizations, locations) from legal documents.
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
  #   case EventBus.request("ediscovery.extract_entities", request, timeout: 10_000) do
  #     {:ok, %{"entities" => entities}} -> {:ok, entities}
  #     error -> error
  #   end
  # end

  defp send_via_http(content, _ctx) do
    url = System.get_env("EDISCOVERY_API_URL", "http://localhost:8001/api/ediscovery/process")
    
    body = Jason.encode!(%{
      emails: [
        %{
          subject: "Entity Extraction Request",
          body: content
        }
      ]
    })

    case HTTPoison.post(url, body, [{"Content-Type", "application/json"}], timeout: 60_000, recv_timeout: 60_000) do
      {:ok, %{status_code: 200, body: resp_body}} ->
        case Jason.decode(resp_body) do
          {:ok, %{"results" => [result | _]}} -> 
            entities = Map.get(result, "entities", [])
            {:ok, %{entities: parse_entities(entities)}}
          _ -> 
            {:error, "Invalid response format"}
        end
      
      error ->
        Logger.error("HTTP request failed: #{inspect(error)}")
        {:error, "Failed to extract entities"}
    end
  end

  defp parse_entities(entities) when is_list(entities) do
    Enum.map(entities, fn entity ->
      %{
        name: Map.get(entity, "name"),
        type: Map.get(entity, "type"),
        relevance: Map.get(entity, "relevance", "unknown")
      }
    end)
  end
  
  defp parse_entities(_), do: []

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