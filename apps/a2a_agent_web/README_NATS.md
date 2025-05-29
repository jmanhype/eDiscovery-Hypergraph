# NATS Event Streaming Integration

This project uses [NATS](https://nats.io/) for distributed event streaming between agents and workflows.

## Running a Local NATS Server

You must have a running NATS server to use the event streaming features and to run integration tests.

### With Docker (Recommended)
```sh
docker run -p 4222:4222 nats:2
```

### With Homebrew (macOS)
```sh
brew install nats-server
nats-server
```

The default connection is to `localhost:4222`. You can configure this in `config/config.exs` under the `:a2a_agent_web, :nats` key.

## Running Integration Tests

Integration tests for event streaming are located in:
- `test/a2a_agent_web_web/event_bus_integration_test.exs`

To run the test:
```sh
mix test test/a2a_agent_web_web/event_bus_integration_test.exs
```

You should see output confirming that events are published and received via NATS.

## Troubleshooting
- **Test fails with `NATS connection (:a2a_nats) is not running!`**: Make sure your NATS server is running and accessible at `localhost:4222`.
- **Test fails with connection refused or timeout**: Check Docker or Homebrew logs, and ensure port 4222 is not blocked.
- **CI/CD**: In your CI pipeline, ensure a NATS server is started before running tests (e.g., via Docker Compose or a service container).

## More Info
- [NATS Documentation](https://docs.nats.io/)
- [Elixir Gnat Library](https://hexdocs.pm/gnat/readme.html)

---

For questions or deeper troubleshooting, check the logs for `[EventBus]` messages, which provide detailed connection and error information.
