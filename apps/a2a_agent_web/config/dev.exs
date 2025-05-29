import Config

config :a2a_agent_web, :nats,
  host: "localhost",
  port: 4222

port_val = String.to_integer(System.get_env("PORT") || "4000")
IO.puts("[dev.exs] Phoenix endpoint will bind to port: #{port_val}")
config :a2a_agent_web, A2aAgentWebWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: port_val]
