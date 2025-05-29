defmodule A2aAgentWeb.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Start PubSub first so it is available for subscriptions
      {Phoenix.PubSub, name: A2aAgentWeb.PubSub},
      # Start the AgentRegistry for dynamic agent discovery
      A2aAgentWebWeb.AgentRegistry,
      # Start the PubSub handler for distributed registry
      A2aAgentWebWeb.AgentRegistryPubSubHandler,
      # Start the NATS event bus for distributed event streaming
      A2aAgentWebWeb.EventBus,
      A2aAgentWebWeb.Telemetry,
      # Start the Finch HTTP client for sending emails
      {Finch, name: A2aAgentWeb.Finch},
      # Start Goldrush event bus and handlers
      A2aAgentWebWeb.GoldrushSupervisor,
      # Start to serve requests, typically the last entry
      A2aAgentWebWeb.Endpoint
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: A2aAgentWeb.Supervisor]
    # Register Prometheus metrics at app startup
    A2aAgentWebWeb.Metrics.setup()
    # Setup OpenTelemetry Phoenix integration
    :ok = OpentelemetryPhoenix.setup()
    # Setup Goldrush event handlers
    :ok = A2aAgentWebWeb.GoldrushHandlers.setup_handlers()
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    A2aAgentWebWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
