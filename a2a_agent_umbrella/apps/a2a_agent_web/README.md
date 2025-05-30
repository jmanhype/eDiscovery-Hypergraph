# A2A Agent Web

This is the Phoenix web/API app for the Hypergraph Agents umbrella. It exposes HTTP endpoints for agent orchestration, story generation, summarization, and A2A protocol operations.

## Key Endpoints
- `POST /api/story` — Generate a story using an LLM (see StoryController)
- `POST /api/summarize` — Summarize text using an LLM (see SummarizerController)
- `POST /api/a2a` — Send A2A protocol messages (task requests, agent discovery, negotiation, etc.)
- `GET /metrics` — Prometheus metrics endpoint
- `GET /status` — Health/status check

## Development
- Run `mix setup` to install dependencies
- Start the Phoenix server with `mix phx.server`
- Visit [localhost:4000](http://localhost:4000) for the API

## Architecture
- Integrates with the core agent and orchestrator apps
- Implements workflow execution, event streaming (NATS), and observability
- See the main [README](../../README.md) for full architecture
