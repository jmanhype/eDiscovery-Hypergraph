defmodule A2aAgentWebWeb.AgentCard do
  @moduledoc """
  Defines the Agent Card schema for agent discovery and negotiation.
  Follows the PRD: includes id, name, version, description, capabilities, endpoints, and authentication info.
  """

  @derive Jason.Encoder
  @enforce_keys [:id, :name, :version, :description, :capabilities, :endpoints]
  defstruct [
    :id,
    :name,
    :version,
    :description,
    :capabilities,   # List of skills/capabilities
    :endpoints,      # Map or list of endpoint URLs/types
    :authentication  # Map or struct for auth info (optional)
  ]

  @type t :: %__MODULE__{
          id: String.t(),
          name: String.t(),
          version: String.t(),
          description: String.t(),
          capabilities: [String.t()],
          endpoints: %{optional(String.t()) => String.t()},
          authentication: map() | nil
        }

  @doc """
  Build an Agent Card from config or runtime info.
  """
  @spec build() :: t()
  def build do
    %__MODULE__{
      id: Application.get_env(:a2a_agent_web, :agent_id, "agent1"),
      name: Application.get_env(:a2a_agent_web, :agent_name, "A2A Agent"),
      version: Application.get_env(:a2a_agent_web, :agent_version, "0.1.0"),
      description: Application.get_env(:a2a_agent_web, :agent_description, "Phoenix A2A agent interface"),
      capabilities: Application.get_env(:a2a_agent_web, :agent_capabilities, ["task_request", "negotiation", "result", "agent_discovery"]),
      endpoints: Application.get_env(:a2a_agent_web, :agent_endpoints, %{"a2a" => "/api/a2a", "agent_card" => "/api/agent_card"}),
      authentication: Application.get_env(:a2a_agent_web, :agent_authentication, nil)
    }
  end
end
