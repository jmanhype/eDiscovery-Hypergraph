# HypergraphAgent

This app is the orchestrator and workflow manager for agentic tasks in the Hypergraph Agents framework.

## Purpose
- Coordinates execution of operators and agents across workflows
- Manages workflow graphs, dependencies, and execution order
- Integrates with Engine (XCS) for graph-based execution and Operator for computational units

## Architecture & Features
- **Orchestration:**
  - Receives workflow/task requests (from API, agents, or external sources)
  - Builds and manages workflow graphs (DAGs)
  - Resolves dependencies and schedules execution
- **Integration:**
  - Delegates execution to Engine (XCS)
  - Uses Operator app for LLM, Map, Sequence, Parallel, and custom operators
  - Works with Agent Registry for agent discovery and assignment
- **Extensible:**
  - Add new orchestration strategies or workflow types in `lib/hypergraph_agent/`

## Example Orchestration Flow
```elixir
# Define a workflow graph (DAG)
graph = %{
  nodes: [
    %{id: :input, op: :input},
    %{id: :summarize, op: :llm, depends_on: [:input]},
    %{id: :output, op: :output, depends_on: [:summarize]}
  ],
  edges: [
    %{from: :input, to: :summarize},
    %{from: :summarize, to: :output}
  ]
}

# Orchestrate the workflow
task_id = "task-123"
result = HypergraphAgent.orchestrate(graph, agent_map, input, task_id: task_id)
```

## Extending the Orchestrator
- Add new orchestration logic or workflow types in `lib/hypergraph_agent/`
- Integrate with additional operator types or external agents
- Implement custom scheduling, monitoring, or logging

## Related Docs
- [Engine App (XCS)](../engine/README.md)
- [Operator App (Operators, Specs)](../operator/README.md)
- [Umbrella README](../../a2a_agent_umbrella/README.md)

---

For architecture, usage, and API details, see the main [README](../../README.md).

