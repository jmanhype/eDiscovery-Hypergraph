defmodule A2aAgent.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      {DNSCluster, query: Application.get_env(:a2a_agent, :dns_cluster_query) || :ignore},
      {Phoenix.PubSub, name: A2aAgent.PubSub},
      # Start the Finch HTTP client for sending emails
      {Finch, name: A2aAgent.Finch}
      # Start a worker by calling: A2aAgent.Worker.start_link(arg)
      # {A2aAgent.Worker, arg}
    ]

    Supervisor.start_link(children, strategy: :one_for_one, name: A2aAgent.Supervisor)
  end
end
