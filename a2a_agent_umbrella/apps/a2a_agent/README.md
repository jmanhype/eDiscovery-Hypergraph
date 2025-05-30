# A2A Agent

This app implements the core Elixir agent logic for the Hypergraph Agents framework. It handles the A2A protocol, agent registry, and message validation for distributed workflows.

## Purpose
- Implements the A2A (Agent-to-Agent) protocol for secure, structured communication between agents
- Provides foundational agent behaviors (registration, discovery, negotiation, task execution)
- Validates and serializes agent messages
- Acts as the core logic for the web API, orchestrator, and other agentic apps

## Architecture & Features
- **A2A Protocol**: Message schema, validation, and negotiation
- **Agent Registry**: Tracks registered agents and their capabilities
- **Specification Protocol**: Input/output validation (see Operator app for details)
- **Extensible**: Add new agent behaviors and protocol extensions as needed
- **Integration**: Used as a dependency by `a2a_agent_web` and `hypergraph_agent`

## Configuration
- Most configuration is managed via the umbrella root
- Environment variables may control logging, protocol options, and registry behavior

## Example Usage
Register an agent and send a task request:

```elixir
# Register agent
A2aAgent.Registry.register(%{id: "agent1", capabilities: ["summarize", "story"]})

# Send a task request message
msg = %{
  type: "task_request",
  sender: "agent1",
  recipient: "agent2",
  payload: %{task_id: "t1", graph: %{nodes: [], edges: []}},
  timestamp: DateTime.utc_now() |> DateTime.to_iso8601()
}
A2aAgent.Protocol.send_message(msg)
```

## Extending the Agent
- Implement new protocol message types by adding handlers in `lib/a2a_agent/protocol/`
- Add registry features in `lib/a2a_agent/registry/`
- See the Operator app for extending input/output validation

## Related Docs
- [A2A Agent Web (API)](../a2a_agent_web/README.md)
- [Operator App (Operators, Specs)](../../operator/README.md)
- [Umbrella README](../../README.md)

---

For architecture, API, and protocol details, see the main [README](../../README.md).
