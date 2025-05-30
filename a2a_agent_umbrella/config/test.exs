import Config

# We don't run a server during test. If one is required,
# you can enable the server option below.
config :a2a_agent_web, A2aAgentWeb.Endpoint,
  http: [ip: {127, 0, 0, 1}, port: 4002],
  secret_key_base: "k02bzMKaW3mQXvpPHl4+wNdhCJ85No5GIOjn1ooVFG1Or+0Ltk4Sm745lZB464JV",
  server: false

# Print only warnings and errors during test
config :logger, level: :warning

# In test we don't send emails
config :a2a_agent, A2aAgent.Mailer, adapter: Swoosh.Adapters.Test

# Disable swoosh api client as it is only required for production adapters
config :swoosh, :api_client, false

# Initialize plugs at runtime for faster test compilation
config :phoenix, :plug_init_mode, :runtime
