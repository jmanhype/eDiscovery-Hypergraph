defmodule A2aAgentWebWeb.Operators.LLMOperator do
  @moduledoc """
  Executes a language model with a formatted prompt using the OpenAI API.
  Returns {:ok, story} or {:error, reason}.
  """

  @openai_url "https://api.openai.com/v1/chat/completions"

  @doc """
  Orchestrator entrypoint: delegates to run/2.
  """
  @spec call(map()) :: {:ok, any()} | {:error, any()}
  @spec call(map()) :: {:ok, any()} | {:error, any()}
  def call(input), do: run(input, %{})
  @moduledoc """
  Executes a language model with a formatted prompt.
  Ember port: LLMOperator. Uses instructor_ex for LLM calls.
  """
  @spec run(map(), any()) :: {:ok, String.t()} | {:error, String.t()}
  @spec run(map(), any()) :: {:ok, String.t()} | {:error, String.t()}
  def run(%{"prompt_template" => prompt_template, "context" => context}, _opts) do
    api_key = System.get_env("OPENAI_API_KEY")
    prompt = :io_lib.format(prompt_template, Map.values(context)) |> IO.iodata_to_binary()
    require Logger
    Logger.info("LLMOperator.run/2 prompt: #{inspect(prompt)}")
    if is_nil(api_key) or api_key == "" do
      Logger.error("OpenAI API key is missing")
      {:error, "OpenAI API key is missing"}
    else
      headers = [
        {"Authorization", "Bearer #{api_key}"},
        {"Content-Type", "application/json"}
      ]
      body = %{
        model: "gpt-4o",
        messages: [%{role: "user", content: prompt}]
      } |> Jason.encode!()
      Logger.info("LLMOperator.run/2 sending request to OpenAI: #{inspect(body)}")
      case HTTPoison.post(@openai_url, body, headers, recv_timeout: 30_000) do
        {:ok, %HTTPoison.Response{status_code: 200, body: resp_body}} ->
          Logger.info("LLMOperator.run/2 OpenAI response: #{String.slice(resp_body, 0, 500)}")
          case Jason.decode(resp_body) do
            {:ok, %{"choices" => [%{"message" => %{"content" => story}} | _]}} ->
              {:ok, story}
            other ->
              Logger.error("LLMOperator.run/2 Could not parse OpenAI response: #{inspect(other)}")
              {:error, "Could not parse OpenAI response"}
          end
        {:ok, %HTTPoison.Response{status_code: code, body: resp_body}} ->
          Logger.error("LLMOperator.run/2 OpenAI API error #{code}: #{resp_body}")
          {:error, "OpenAI API error #{code}: #{resp_body}"}
        {:error, reason} ->
          Logger.error("LLMOperator.run/2 HTTPoison error: #{inspect(reason)}")
          {:error, inspect(reason)}
      end
    end
  end
end
