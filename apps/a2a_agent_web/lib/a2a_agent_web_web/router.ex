defmodule A2aAgentWebWeb.Router do
  @moduledoc """
  The main router for the A2aAgentWebWeb application.
  """
  use A2aAgentWebWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", A2aAgentWebWeb do
    pipe_through :browser
    get "/", PageController, :index
    # Prometheus metrics endpoint at root
    get "/metrics", MetricsController, :metrics
  end

  scope "/api", A2aAgentWebWeb do
    pipe_through :api

    # Orchestration endpoint
    post "/a2a", AgentController, :a2a

    # Simulation endpoint
    post "/simulate_workflow", SimulationController, :simulate

    # Summarization endpoint
    post "/summarize", SummarizerController, :summarize
    post "/story", StoryController, :create

    # Health/status endpoint
    get "/status", StatusController, :status

    # Agent card endpoints
    get "/agent_card", AgentController, :agent_card
    post "/agent_card", AgentController, :register_agent
    get "/agent_card/:id", AgentController, :get_agent

    # Agent registry endpoint
    get "/agent_registry", AgentController, :list_agents

    # Unregister agent endpoint
    delete "/agent_card/:id", AgentController, :unregister_agent

    # Operator introspection endpoints
    get "/operators", OperatorsController, :index
    get "/operators/:name", OperatorsController, :show

    # Model introspection endpoint
    get "/models", ModelsController, :index

    # Prometheus metrics endpoint
    get "/metrics", MetricsController, :metrics
  end
end