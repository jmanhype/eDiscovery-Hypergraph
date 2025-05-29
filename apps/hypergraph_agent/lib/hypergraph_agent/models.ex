defmodule HypergraphAgent.Models do
  @moduledoc """
  Central registry and interface for all LLMs and models used in the system.
  Inspired by EmberEx.Models, this module provides a unified way to access, list, and invoke models
  from any part of the umbrella project (operators, orchestrator, API, etc).
  """

  require Logger

  @typedoc "Function type for model callables"
  @type model_callable :: (String.t() -> map())

  @providers %{
    "openai" => %{
      prefix: "openai:",
      model_versions: %{
        "gpt-3.5-turbo" => "gpt-3.5-turbo-0125",
        "gpt-4" => "gpt-4-0125-preview",
        "gpt-4o" => "gpt-4o-2024-05-13"
      }
    },
    "anthropic" => %{
      prefix: "anthropic:",
      model_versions: %{
        "claude-3" => "claude-3-opus-20240229"
      }
    }
  }

  @doc """
  List all available models and their metadata.
  """
  @spec list_models() :: [%{provider: String.t(), model: String.t(), version: String.t()}]
  def list_models do
    Enum.flat_map(@providers, fn {provider, config} ->
      Enum.map(config.model_versions, fn {base, version} ->
        %{provider: provider, model: base, version: version}
      end)
    end)
  end

  @doc """
  Get a callable for the given model ID (e.g., "gpt-4o" or "openai:gpt-4o").
  Returns a function that takes a prompt and returns a map/struct result.
  """
  @spec model(String.t(), keyword()) :: model_callable()
  def model(model_id, config \\ []) do
    {provider, api_model_id} = resolve_model_for_api(model_id)
    fn prompt ->
      Logger.info("Calling model #{provider}:#{api_model_id}")
      # Stub: Replace with real API call (e.g., instructor_ex, HTTP client, etc)
      %{result: "[stubbed result from #{provider}:#{api_model_id} for prompt: #{prompt}]"}
    end
  end

  @doc """
  Resolve a model ID to provider and version, handling prefixes and defaults.
  """
  @spec resolve_model_for_api(String.t()) :: {String.t(), String.t()}
  def resolve_model_for_api(model_id) do
    case model_id do
      "openai:" <> rest -> resolve_model_version("openai", rest)
      "anthropic:" <> rest -> resolve_model_version("anthropic", rest)
      _ -> resolve_model_version("openai", model_id)
    end
  end

  @doc """
  Resolve a specific model version for a provider.
  """
  @spec resolve_model_version(String.t(), String.t()) :: {String.t(), String.t()}
  def resolve_model_version(provider, model_base) do
    provider_config = Map.get(@providers, provider, %{model_versions: %{}})
    version = Map.get(provider_config.model_versions, model_base, model_base)
    {provider, version}
  end
end
