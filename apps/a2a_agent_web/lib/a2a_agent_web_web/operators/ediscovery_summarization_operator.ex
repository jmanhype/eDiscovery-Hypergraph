defmodule A2aAgentWebWeb.Operators.EdiscoverySummarizationOperator do
  @moduledoc """
  Operator for summarizing legal documents in eDiscovery workflows.
  Communicates with Python backend via NATS or falls back to direct API.
  """

  # alias A2aAgentWebWeb.EventBus # TODO: Enable when EventBus supports request/reply
  require Logger

  @spec run(any(), map()) :: {:ok, map()} | {:error, String.t()}
  def run(input, ctx) do
    Logger.info("EdiscoverySummarizationOperator received input: #{inspect(input)}")
    email_content = get_email_content(input)
    Logger.info("Extracted email content: #{inspect(email_content)}")
    
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
  #   case EventBus.request("ediscovery.summarize", request, timeout: 10_000) do
  #     {:ok, %{"summary" => summary}} -> {:ok, summary}
  #     error -> error
  #   end
  # end

  defp send_via_http(content, _ctx) do
    url = System.get_env("EDISCOVERY_API_URL", "http://localhost:8001/api/ediscovery/process")
    
    Logger.info("Sending content to backend: #{String.slice(content, 0, 100)}...")
    
    body = Jason.encode!(%{
      emails: [
        %{
          subject: "Document Analysis Request",
          body: content
        }
      ]
    })

    case HTTPoison.post(url, body, [{"Content-Type", "application/json"}], timeout: 60_000, recv_timeout: 60_000) do
      {:ok, %{status_code: 200, body: resp_body}} ->
        case Jason.decode(resp_body) do
          {:ok, %{"results" => [result | _]}} -> 
            {:ok, %{summary: Map.get(result, "summary", "No summary available")}}
          _ -> 
            {:error, "Invalid response format"}
        end
      
      error ->
        Logger.error("HTTP request failed: #{inspect(error)}")
        {:error, "Failed to summarize document"}
    end
  end

  # TODO: Uncomment when EventBus supports request/reply
  # defp generate_email_id do
  #   "email_#{:os.system_time(:millisecond)}_#{:rand.uniform(1000)}"
  # end

  @doc """
  Workflow engine compatibility - receives merged input
  """
  @spec call(map()) :: map()
  def call(input) do
    Logger.info("EdiscoverySummarizationOperator.call received: #{inspect(input)}")
    case run(input, %{}) do
      {:ok, result} -> result
      {:error, reason} -> %{error: reason}
    end
  end
end