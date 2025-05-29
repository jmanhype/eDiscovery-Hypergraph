defmodule A2aAgentWebWeb.MyOpenAISummarizerAgent do
  @moduledoc """
  Agent that summarizes input text using OpenAI GPT-4o.
  Implements before_node/4 for orchestration integration.
  """
  @openai_url "https://api.openai.com/v1/chat/completions"
  @doc """
  OpenAI API key, must be set in the environment as OPENAI_API_KEY.
  Do NOT hardcode secrets in source code.
  """
  @api_key System.get_env("OPENAI_API_KEY")

  @doc """
  Adds a summary to the input by calling OpenAI GPT-4o.
  """
  @spec before_node(any(), map(), module(), map()) :: map()
  def before_node(_node, input, _op, _acc) do
    prompt = "Summarize this customer feedback: #{input["text"]}"
    if is_nil(@api_key) or @api_key == "" do
      require Logger
      Logger.warning("OPENAI_API_KEY environment variable is not set. Summarization will not work.")
      Map.put(input, "summary", "API key missing")
    else
      headers = [
        {"Authorization", "Bearer #{@api_key}"},
        {"Content-Type", "application/json"}
      ]
      body = %{
        model: "gpt-4o",
        messages: [%{role: "user", content: prompt}]
      } |> Jason.encode!()

      case HTTPoison.post(@openai_url, body, headers) do
        {:ok, %HTTPoison.Response{status_code: 200, body: resp_body}} ->
          case Jason.decode(resp_body) do
            {:ok, %{"choices" => [%{"message" => %{"content" => summary}} | _]}} ->
              Map.put(input, "summary", summary)
            _ ->
              Map.put(input, "summary", "Could not parse OpenAI response")
          end
        _ ->
          Map.put(input, "summary", "Could not generate summary")
      end
    end
  end

  @doc """
  Passes output through unchanged.
  """
  @spec after_node(any(), map(), module(), map()) :: map()
  def after_node(_node, output, _op, _acc), do: output
end
