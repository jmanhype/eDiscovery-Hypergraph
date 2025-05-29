defmodule A2aAgentWeb.MixProject do
  use Mix.Project

  def project do
    [
      app: :a2a_agent_web,
      version: "0.1.0",
      build_path: "../../_build",
      config_path: "../../config/config.exs",
      deps_path: "../../deps",
      lockfile: "../../mix.lock",
      elixir: "~> 1.14",
      elixirc_paths: elixirc_paths(Mix.env()),
      start_permanent: Mix.env() == :prod,
      aliases: aliases(),
      deps: deps()
    ]
  end

  # Configuration for the OTP application.
  #
  # Type `mix help compile.app` for more information.
  def application do
    [
      mod: {A2aAgentWeb.Application, []},
      extra_applications: [:logger, :runtime_tools, :goldrush]
    ]
  end

  # Specifies which paths to compile per environment.
  defp elixirc_paths(:test), do: ["lib", "test/support"]
  defp elixirc_paths(_), do: ["lib"]

  # Specifies your project dependencies.
  #
  # Type `mix help deps` for examples and options.
  defp deps do
    [
      {:finch, "~> 0.16"},
      {:swoosh, "~> 1.5"},
      {:phoenix, "~> 1.7.0"},
      {:phoenix_pubsub, "~> 2.1"},
      {:phoenix_html, "~> 3.3"},
      {:phoenix_live_reload, "~> 1.4", only: :dev},
      {:phoenix_live_view, "~> 0.19.5"},
      {:floki, ">= 0.34.0", only: :test},
      {:telemetry_metrics, "~> 1.1"},
      {:telemetry_poller, "~> 1.0"},
      {:gettext, "~> 0.20"},
      {:jason, "~> 1.2"},
      {:httpoison, "~> 1.8"},
      {:plug_cowboy, "~> 2.5"},
      {:bandit, "~> 1.0"},
      {:prometheus_ex, "~> 3.0"},
      {:prometheus_plugs, "~> 1.1"},
      {:opentelemetry, "~> 1.4"},
      {:opentelemetry_api, "~> 1.1"},
      {:opentelemetry_exporter, "~> 1.6"},
      {:opentelemetry_phoenix, "~> 1.1"},
      {:goldrush, github: "jmanhype/goldrush", branch: "telemetry-plugins-integrated"},
      {:hypergraph_agent, in_umbrella: true},
      {:gnat, "~> 1.5"}, # NATS client for distributed event streaming
      {:yaml_elixir, "~> 2.4"}
    ]
  end

  # Aliases are shortcuts or tasks specific to the current project.
  # For example, to install project dependencies and perform other setup tasks, run:
  #
  #     $ mix setup
  #
  # See the documentation for `Mix` for more info on aliases.
  defp aliases do
    [
      setup: ["deps.get"]
    ]
  end
end
