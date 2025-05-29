defmodule A2aAgentWebWeb.Operators.EdiscoveryProcessOperator do
  @moduledoc """
  Single operator that processes legal documents through the full eDiscovery pipeline.
  Returns complete analysis including summary, classification, and entities.
  """

  require Logger

  @spec run(any(), map()) :: {:ok, map()} | {:error, String.t()}
  def run(input, ctx) do
    Logger.info("EdiscoveryProcessOperator received input: #{inspect(input)}")
    email_content = get_email_content(input)
    Logger.info("Extracted email content: #{inspect(email_content)}")
    
    send_via_http(email_content, ctx)
  end

  defp get_email_content(input) when is_map(input) do
    Map.get(input, "email", Map.get(input, "email_text", Map.get(input, "content", "")))
  end
  defp get_email_content(input) when is_binary(input), do: input

  defp send_via_http(content, _ctx) do
    url = System.get_env("EDISCOVERY_API_URL", "http://localhost:8001/api/ediscovery/process")
    
    Logger.info("Sending content to backend for full processing...")
    
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
            {:ok, %{
              summary: Map.get(result, "summary", "No summary available"),
              tags: Map.get(result, "tags", %{}),
              entities: Map.get(result, "entities", [])
            }}
          _ -> 
            {:error, "Invalid response format"}
        end
      
      error ->
        Logger.error("HTTP request failed: #{inspect(error)}")
        {:error, "Failed to process document"}
    end
  end

  @doc """
  Workflow engine compatibility - receives merged input
  """
  @spec call(map()) :: map()
  def call(input) do
    Logger.info("EdiscoveryProcessOperator.call received: #{inspect(input)}")
    case run(input, %{}) do
      {:ok, result} -> result
      {:error, reason} -> %{error: reason}
    end
  end
end