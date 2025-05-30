defmodule A2aAgentWeb.Router do
  use A2aAgentWeb, :router

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/api", A2aAgentWeb do
    pipe_through :api

    get "/agent_card", AgentController, :agent_card
    post "/a2a", AgentController, :a2a
    get "/openapi.yaml", OpenapiController, :spec
    get "/swagger", SwaggerUiController, :index
  end

  # Enable Swoosh mailbox preview in development
  if Application.compile_env(:a2a_agent_web, :dev_routes) do

    scope "/dev" do
      pipe_through [:fetch_session, :protect_from_forgery]

      forward "/mailbox", Plug.Swoosh.MailboxPreview
    end
  end
end
