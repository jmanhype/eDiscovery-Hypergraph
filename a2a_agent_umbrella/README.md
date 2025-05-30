# A2A Agent Umbrella

This directory is the Elixir Mix umbrella for the Hypergraph Agents project. It manages all core Elixir apps and dependencies for the distributed agentic AI system.

## Structure

- **apps/a2a_agent/** — Core agent protocol logic, registry, and validation
- **apps/a2a_agent_web/** — Phoenix API app for HTTP endpoints, orchestration, and event streaming
- **apps/engine/** — Workflow execution engine (XCS), supporting DAGs and parallel execution
- **apps/hypergraph_agent/** — Orchestrator and workflow manager for agentic tasks
- **apps/operator/** — Operator library (LLM, Map, Sequence, Parallel, etc.)

## What is a Mix Umbrella?
A Mix umbrella project allows you to manage multiple interdependent Elixir apps in a single repository. Each app can be developed, tested, and released independently, but dependencies and configuration are managed centrally.

## Responsibilities
- Centralizes configuration and dependency management
- Coordinates development, testing, and release of all core Elixir apps
- Enables modular, scalable architecture for agentic AI workflows

## Development Workflow
1. **Install dependencies:**
   ```sh
   mix deps.get
   ```
2. **Run all tests:**
   ```sh
   mix test
   ```
3. **Start the Phoenix API:**
   ```sh
   cd apps/a2a_agent_web
   mix phx.server
   ```
4. **Develop and test individual apps:**
   ```sh
   cd apps/engine
   mix test
   ```

## Adding a New App
1. Generate a new app:
   ```sh
   mix new apps/my_new_app
   ```
2. Add it as a dependency in other apps' `mix.exs` if needed.
3. Document its purpose and usage in its own `README.md`.

## Dependency Management
- Shared deps are managed in the umbrella's `mix.exs`.
- Each app can declare its own deps in its `mix.exs`.
- Use `mix deps.get` at the umbrella root to sync all dependencies.

## Related Docs
- [Main Project README](../README.md)
- [A2A Agent (core)](apps/a2a_agent/README.md)
- [A2A Agent Web](apps/a2a_agent_web/README.md)
- [Engine](apps/engine/README.md)
- [HypergraphAgent](apps/hypergraph_agent/README.md)
- [Operator](apps/operator/README.md)

---

## Design Inspiration: Wing Chun Trihedron Geometry

This project’s core graph and workflow design draws inspiration from Wing Chun martial art geometry—specifically the use of the **trihedron** (three-pointed structure) pointed both up and down. This form is used in Wing Chun to represent balance, centerline, and dynamic flow, and is reflected in the way agent workflows and hypergraph topologies are structured here. The trihedron provides:

- **Balance and symmetry** in workflow design
- **Clear directional flow** (upward and downward propagation of tasks/data)
- **Strong, modular interconnections** between nodes (agents/operators)

This geometric inspiration helps ensure that the system is both robust and adaptable, mirroring the principles of Wing Chun in computational form.

For architecture, usage, and API details, see the main [README](../README.md).
