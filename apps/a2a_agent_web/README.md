# A2A Agent Web

Phoenix API for the A2A Agent system. Provides endpoints for agent workflows, story generation, summarization, and status/metrics.

## Agent Registry & Discovery

The A2A Agent Web app includes a robust, distributed agent registry and discovery system, enabling dynamic, plug-and-play agent participation across nodes and runtimes.

### `lib/a2a_agent_web_web/agent_registry.ex`

**Purpose:**
- Implements a distributed, in-memory registry for agent discovery and dynamic registration.
- Uses Phoenix.PubSub to synchronize agent presence across nodes.
- Persists registry state to disk for resilience.

**Key Features:**
- **Dynamic Registration:** Agents can register/unregister at runtime using `AgentCard` structs.
- **Distributed Sync:** PubSub ensures all nodes converge on the same registry state.
- **Persistence:** Registry state is saved to disk and restored on startup.
- **Extensible:** New agent types, metadata, or protocols can be added by extending `AgentCard` and registration logic.

**Integration Points:**
- All agent presence/availability is managed here, enabling orchestrators and workflows to discover and utilize agents dynamically.
- External agents (e.g., Python) can participate by registering via the protocol.

**Amplification Opportunities:**
- Extend `AgentCard` with capabilities, health, or protocol info
- Add health checks and liveness monitoring
- Expose REST/gRPC endpoints for cross-language agent registration
- Add authentication/authorization for agent registration

### `lib/a2a_agent_web_web/agent_registry_pubsub_handler.ex`

**Purpose:**
- GenServer that handles PubSub events for the agent registry.
- Delegates all received messages to `AgentRegistry.handle_info/1` for processing.

**Key Features:**
- **Subscription:** Subscribes to the `agent_registry` topic on startup.
- **Delegation:** Forwards all PubSub messages to the registry for state updates and sync.

**Integration Points:**
- Ensures that registry changes (registration, unregistration, sync) propagate cluster-wide in real time.

**Amplification Opportunities:**
- Add monitoring or logging for registry events
- Support for custom event handlers (e.g., for metrics, security)

---

### `lib/a2a_agent_web_web/my_openai_summarizer_agent.ex`

**Purpose:**
- Implements an agent that summarizes input text using OpenAI GPT-4o.
- Integrates with the orchestration system via the `before_node/4` callback, allowing it to process input before a workflow node executes.

**Key Features:**
- **LLM Integration:** Calls the OpenAI API to generate a summary for provided text input.
- **Environment-based Secrets:** Reads the OpenAI API key from the `OPENAI_API_KEY` environment variable for security.
- **Error Handling:** Handles missing API keys and API errors gracefully, logging warnings and providing fallback summaries.
- **Orchestration Hooks:** Implements both `before_node/4` (to inject summaries) and `after_node/4` (pass-through for output), making it compatible with workflow orchestration.

**Integration Points:**
- Can be registered and discovered via the agent registry, making it available for workflows that require LLM summarization.
- Can be composed with other agents or operators in a workflow graph.

**Extensibility Notes:**
- Additional agent behaviors can be implemented by following this pattern (e.g., other LLMs, tools, or APIs).
- Supports further customization of prompts, models, or downstream processing.
- Secure by default (no secrets in code), and easily portable to other environments.

---

### `lib/a2a_agent_web_web/operators/llm_operator.ex`

**Purpose:**
- Implements the LLMOperator, which executes a language model (OpenAI GPT-4o) with a formatted prompt.
- Provides a functional entrypoint for orchestrators and workflows to invoke LLMs as operators.
- Ported from the Ember framework (Python) to Elixir, maintaining compatibility and extensibility.

**Key Features:**
- **Prompt Formatting:** Accepts a prompt template and context, formats the prompt dynamically.
- **LLM API Integration:** Calls the OpenAI API with the formatted prompt and returns the model output.
- **Error Handling & Logging:** Handles missing API keys, API errors, and response parsing issues, with robust logging for observability.
- **Composable Operator:** Can be used as a node in workflow graphs or composed with other operators/agents.

**Integration Points:**
- Used by the orchestrator and workflow engine to execute LLM tasks as part of larger workflows.
- Can be composed with map, sequence, parallel, or custom operators for complex agentic behavior.
- Secure by default (API key from environment), and observable via logging.

**Extensibility Notes:**
- Easily extended to support other LLM providers, models, or prompt strategies.
- Can be wrapped as an agent or used as a building block for higher-level agent behaviors.
- Compatible with dynamic agent/operator discovery and registry mechanisms.

---

### `lib/a2a_agent_web_web/operators/map_operator.ex`

**Purpose:**
- Implements the MapOperator, a functional operator that applies a provided function to an input value and returns the result.
- Ported from the Ember framework (Python) to Elixir, maintaining functional programming idioms.

**Key Features:**
- **Functional Composition:** Accepts any unary function and applies it to the input, enabling flexible data transformation.
- **Minimal Interface:** Simple, single-purpose operator with a clear contract (`run/2`).
- **Composable:** Can be used as a node in workflow graphs or composed with other operators/agents for complex transformations.

**Integration Points:**
- Used by orchestrator and workflow engine to transform data within workflows.
- Can be composed with sequence, parallel, LLM, or custom operators for advanced agentic behaviors.

**Extensibility Notes:**
- Serves as a pattern for implementing other functional or higher-order operators.
- Can be wrapped as an agent or extended to support additional functional paradigms (e.g., map/filter/reduce over collections).
- Compatible with dynamic agent/operator discovery and registry mechanisms.

---

### `lib/a2a_agent_web_web/operators/sequence_operator.ex`

**Purpose:**
- Implements the SequenceOperator, which executes a sequence of operators or functions in order, passing outputs from one to the next.
- Ported from the Ember framework (Python) to Elixir, supporting compositional workflow logic.

**Key Features:**
- **Sequential Composition:** Accepts a list of operators or functions and applies them in order, chaining the output of each to the input of the next.
- **Flexible Input:** Supports both operator and function tuples (`{:op, op}` or `{:fun, fun}`), allowing for mixed composition.
- **Composable:** Enables construction of complex workflows from simple building blocks.

**Integration Points:**
- Used by orchestrator and workflow engine to compose multi-step workflows.
- Can be combined with map, parallel, LLM, or custom operators for advanced agentic behaviors.

**Extensibility Notes:**
- Pattern for implementing other composite operators (e.g., conditional, branching, parallel).
- Can be wrapped as an agent for higher-level workflow logic.
- Compatible with dynamic agent/operator discovery and registry mechanisms.

---

### `lib/a2a_agent_web_web/operators/parallel_operator.ex`

**Purpose:**
- Implements the ParallelOperator, which executes multiple operators or functions concurrently and merges their outputs.
- Ported from the Ember framework (Python) to Elixir, supporting parallel workflow execution.

**Key Features:**
- **Parallel Composition:** Accepts a list of operators or functions, executes each in its own task, and collects their results.
- **Flexible Input:** Supports both operator and function tuples (`{:op, op}` or `{:fun, fun}`), allowing for mixed parallel composition.
- **Composable:** Enables construction of workflows that require concurrent execution of multiple steps.

**Integration Points:**
- Used by orchestrator and workflow engine to enable parallelism in workflows.
- Can be combined with map, sequence, LLM, or custom operators for advanced agentic behaviors.

**Extensibility Notes:**
- Pattern for implementing other parallel or concurrent operators (e.g., scatter-gather, fan-out/fan-in).
- Can be wrapped as an agent for higher-level parallel logic.
- Compatible with dynamic agent/operator discovery and registry mechanisms.

---

### `lib/a2a_agent_web_web/operators/branch_operator.ex`

**Purpose:**
- Implements the BranchOperator, which executes one of several branches based on a predicate function.
- Ported from the Ember framework (Python) to Elixir, supporting conditional logic in workflows.

**Key Features:**
- **Conditional Branching:** Accepts a list of `{predicate, operator}` tuples and executes the first operator whose predicate returns true.
- **Flexible Logic:** Enables dynamic workflow paths based on input data or state.
- **Composable:** Can be used as a node in workflow graphs or combined with other operators for complex branching logic.
- **Example Usage:** See inline doctest for practical usage.

**Integration Points:**
- Used by orchestrator and workflow engine to implement conditional execution paths.
- Can be combined with map, sequence, parallel, LLM, or custom operators for advanced agentic behaviors.

**Extensibility Notes:**
- Pattern for implementing other control-flow operators (e.g., switch, guard, multi-branch).
- Can be wrapped as an agent for higher-level decision logic.
- Compatible with dynamic agent/operator discovery and registry mechanisms.

---

### `lib/a2a_agent_web_web/operators/aggregate_operator.ex`

**Purpose:**
- Implements the AggregateOperator, which aggregates a list of inputs using a reducer function and initial value.
- Ported from the Ember framework (Python) to Elixir, supporting aggregation and reduction patterns in workflows.

**Key Features:**
- **Aggregation/Reduction:** Applies a reducer function to a list of inputs and an initial value, producing a single aggregated result.
- **Order Guarantee:** Explicitly reverses input list to ensure left-to-right reduction, matching Elixir convention and documentation.
- **Composable:** Can be used as a node in workflow graphs or combined with other operators for aggregation logic.
- **Example Usage:** See inline doctest for practical usage.

**Integration Points:**
- Used by orchestrator and workflow engine to aggregate results from parallel or sequential steps.
- Can be combined with map, sequence, parallel, branch, or custom operators for advanced agentic behaviors.

**Extensibility Notes:**
- Pattern for implementing other aggregation or reduction operators (e.g., fold, scan, combine).
- Can be wrapped as an agent for higher-level aggregation logic.
- Compatible with dynamic agent/operator discovery and registry mechanisms.

---

### `lib/a2a_agent_web_web/operators/pass_through_operator.ex`

**Purpose:**
- Implements the PassThroughOperator, which simply returns its input unchanged.
- Provides a no-op operator compatible with orchestrator and workflow systems.

**Key Features:**
- **No-Op Behavior:** Returns the input unchanged, wrapped in `{:ok, input}`.
- **Orchestrator Compatibility:** Implements a `call/1` entrypoint for seamless integration with workflow orchestration systems.
- **Composable:** Can be used as a node in workflow graphs, especially for debugging, testing, or placeholder logic.

**Integration Points:**
- Used by orchestrator and workflow engine as a default or placeholder operator in workflows.
- Can be combined with other operators for testing, debugging, or as a base for new operator development.

**Extensibility Notes:**
- Serves as a pattern for implementing other simple or identity operators.
- Can be wrapped as an agent for higher-level workflow logic or for scaffolding new operator types.
- Compatible with dynamic agent/operator discovery and registry mechanisms.

---

### `lib/a2a_agent_web_web/controllers/summarizer_controller.ex`

**Purpose:**
- Implements the SummarizerController, handling HTTP requests for text summarization and story generation using LLMs (OpenAI GPT-4o).
- Provides API endpoints for `/api/summarize` and `/api/story`, integrating with the orchestration system.

**Key Features:**
- **LLM Orchestration:** Builds and executes workflow graphs using the orchestrator and LLMOperator for both summarization and story generation.
- **Flexible Input Handling:** Accepts JSON input, constructs prompt templates and context dynamically.
- **Robust Result Handling:** Handles multiple result shapes from orchestrator, with comprehensive error logging and HTTP responses.
- **Extensible Design:** Easily supports new endpoints or LLM-based transformations by following the established orchestration pattern.

**Integration Points:**
- Invokes the orchestrator (`HypergraphAgent.BasicOrchestrator.orchestrate/3`) with workflow graphs and agent maps.
- Utilizes LLMOperator and other operators as workflow nodes.
- Part of the web API layer, exposing LLM services to external clients.

**Extensibility Notes:**
- Can be extended to support additional LLM-based endpoints, custom operators, or more complex workflow graphs.
- Error handling and response logic can be adapted for new result shapes as orchestration evolves.
- Follows Phoenix and Elixir idioms, making it easy for contributors to maintain or enhance.

---

### `lib/a2a_agent_web_web/controllers/agent_controller.ex`

**Purpose:**
- Implements the AgentController, handling HTTP endpoints for agent card discovery, registration, unregistration, listing, and advanced A2A protocol messaging.
- Acts as the main integration point for agent registry, discovery, negotiation, and task orchestration in the A2A Agent system.

**Key Features:**
- **Agent Registry Integration:** Endpoints for registering, unregistering, listing, and fetching agent cards, tightly integrated with the distributed AgentRegistry.
- **A2A Protocol Handling:** Receives, validates, and processes A2A protocol messages (negotiation, agent discovery, task requests, etc.) with orchestrator and metrics instrumentation.
- **Streaming & Chunked Responses:** Supports streaming task results and chunked responses for long-running or streaming workflows.
- **Observability:** Integrates with OpenTelemetry, GoldrushEx, and custom metrics for tracing, logging, and monitoring all protocol and registry operations.
- **Robust Error Handling:** Comprehensive validation, error reporting, and fallback logic for malformed or unexpected messages.

**Integration Points:**
- Directly interacts with AgentRegistry, Orchestrator, Metrics, NegotiationHandler, and A2AMessage schema.
- Exposes REST endpoints for agent lifecycle and protocol operations, enabling dynamic agent participation and orchestration.
- Provides hooks for external agents (e.g., Python) to register and communicate via the protocol.

**Extensibility Notes:**
- Designed for extensibility: new protocol types, agent metadata, or orchestration patterns can be added with minimal friction.
- Metrics and tracing hooks can be expanded for deeper observability or integration with external monitoring systems.
- Follows Phoenix and Elixir idioms for maintainability and contributor onboarding.

---

### `lib/a2a_agent_web_web/controllers/story_controller.ex`

**Purpose:**
- Implements the StoryController, handling HTTP requests for LLM-based story generation.
- Provides the `/api/story` endpoint, integrating with the orchestration system and LLMOperator.

**Key Features:**
- **LLM Orchestration:** Constructs and executes workflow graphs using the orchestrator and LLMOperator for story generation.
- **Flexible Input Handling:** Accepts JSON input, dynamically constructs prompt templates and context for LLMs.
- **Robust Result Handling:** Handles multiple result shapes from orchestrator, with comprehensive error logging and HTTP responses.
- **Extensible Design:** Easily supports new endpoints or LLM-based transformations by following the established orchestration pattern.

**Integration Points:**
- Invokes the orchestrator (`HypergraphAgent.BasicOrchestrator.orchestrate/3`) with workflow graphs and agent maps.
- Utilizes LLMOperator and other operators as workflow nodes.
- Part of the web API layer, exposing LLM story generation to external clients.

**Extensibility Notes:**
- Can be extended to support additional LLM-based endpoints, custom operators, or more complex workflow graphs.
- Error handling and response logic can be adapted for new result shapes as orchestration evolves.
- Follows Phoenix and Elixir idioms for maintainability and contributor onboarding.

---

### `lib/a2a_agent_web_web/controllers/simulation_controller.ex`

**Purpose:**
- Implements the SimulationController, handling HTTP requests for simulating LLM-generated workflow graphs.
- Provides endpoints for simulating and validating workflow graphs based on user-provided workflow text and input.

**Key Features:**
- **Workflow Parsing:** Uses `WorkflowParser` to parse workflow text into nodes and edges, supporting dynamic, user-defined workflows.
- **Operator Normalization:** Dynamically maps operator identifiers to their module implementations, supporting all core operators (LLM, Map, Sequence, Parallel, Branch, Aggregate, PassThrough).
- **Graph Construction:** Builds workflow graphs from parsed nodes and edges, supporting dependency resolution and parameter normalization.
- **Engine Integration:** Invokes the `Engine.run/2` function to execute the constructed workflow graph with input.
- **Robust Error Handling:** Handles parsing errors, unknown operators, and invalid workflow formats with clear error responses.

**Integration Points:**
- Interfaces with `Engine` for graph execution and `WorkflowParser` for workflow parsing.
- Supports all core operator modules for dynamic workflow simulation.
- Part of the web API layer, exposing workflow simulation capabilities to external clients.

**Extensibility Notes:**
- Can be extended to support additional operator types, custom workflow formats, or enhanced simulation features.
- Error handling and operator normalization can be adapted as new operators or workflow patterns are introduced.
- Follows Phoenix and Elixir idioms for maintainability and contributor onboarding.

---

### `lib/a2a_agent_web_web/controllers/metrics_controller.ex`

**Purpose:**
- Implements the MetricsController, exposing Prometheus metrics at the `/metrics` endpoint.
- Provides an integration point for observability and monitoring infrastructure.

**Key Features:**
- **Prometheus Integration:** Formats and returns all Prometheus metrics in plain text for scraping by Prometheus servers.
- **Simple API:** Single endpoint for metrics, following Prometheus conventions and best practices.
- **Extensible:** Can be extended to expose additional or custom metrics as needed.

**Integration Points:**
- Interfaces with the Prometheus Elixir library for metric formatting and collection.
- Part of the web API layer, enabling integration with Prometheus and other monitoring tools.

**Extensibility Notes:**
- Can be extended to support additional metrics, custom exporters, or new observability endpoints.
- Follows Phoenix and Elixir idioms for maintainability and contributor onboarding.

---

### `lib/a2a_agent_web_web/my_openai_summarizer_agent.ex`

**Purpose:**
- Implements the MyOpenAISummarizerAgent, an agent that summarizes input text using OpenAI GPT-4o.
- Integrates with the orchestration system via the `before_node/4` callback, enabling LLM summarization as part of workflow execution.

**Key Features:**
- **LLM Integration:** Calls the OpenAI API to generate a summary for provided text input.
- **Environment-based Secrets:** Reads the OpenAI API key from the `OPENAI_API_KEY` environment variable for security; does not hardcode secrets.
- **Error Handling:** Handles missing API keys and API errors gracefully, logging warnings and providing fallback summaries.
- **Orchestration Hooks:** Implements both `before_node/4` (to inject summaries) and `after_node/4` (pass-through for output), making it compatible with orchestration frameworks.

**Integration Points:**
- Can be registered and discovered via the agent registry, making it available for workflows that require LLM summarization.
- Can be composed with other agents or operators in workflow graphs.

**Extensibility Notes:**
- Additional agent behaviors can be implemented by following this pattern (e.g., other LLMs, tools, or APIs).
- Supports further customization of prompts, models, or downstream processing.
- Secure by default (no secrets in code), and easily portable to other environments.

---

### `apps/engine/lib/engine.ex`

**Purpose:**
- Implements the Hypergraph Execution Engine (XCS) for multi-agent workflows, ported from Ember (Python) to Elixir.
- Provides graph-based execution, supporting dependency resolution, parallelization, and topological sorting.

**Key Features:**
- **Graph-based Execution:** Executes operator graphs with support for both sequential and parallel execution modes.
- **Topological Sorting:** Resolves dependencies between nodes using topological sort to determine execution order.
- **Parallelization:** Groups nodes by dependency depth for efficient parallel execution where possible.
- **Specification Protocol Integration:** Optionally validates input/output against node specifications for correctness.
- **Composable and Extensible:** Designed to support arbitrary operators, specifications, and flexible graph shapes.

**Integration Points:**
- Invoked by controllers and orchestration layers to execute workflow graphs.
- Compatible with all operator modules and agents following the operator protocol.
- Can be extended to support additional execution strategies or metrics instrumentation.

**Extensibility Notes:**
- New execution modes, scheduling strategies, or instrumentation can be added with minimal impact to core logic.
- Specification validation can be expanded for richer input/output checking.
- Modular design enables integration with new operator types, agents, or orchestration patterns.

---

### `apps/engine/lib/workflow_parser.ex`

**Purpose:**
- Implements the WorkflowParser, which parses LLM-generated workflow text into a workflow graph structure (nodes and edges).
- Enables dynamic, user-defined workflow construction for orchestration and simulation.

**Key Features:**
- **Flexible Parsing:** Extracts nodes (with IDs, operators, and dependencies) and edges from YAML-like workflow text.
- **Robust Regex Extraction:** Uses regular expressions to parse node and edge definitions, supporting both simple and dependent nodes.
- **Atom-safe Mapping:** Converts all node and dependency identifiers to atoms for efficient graph construction and execution.
- **Standardized Output:** Returns a map with `:nodes` and `:edges` for downstream processing by the engine or controllers.

**Integration Points:**
- Used by the simulation controller and other orchestration components to convert user/LLM-generated text into executable workflow graphs.
- Compatible with the execution engine (XCS) and operator modules.

**Extensibility Notes:**
- Can be extended to support additional workflow formats, richer node/edge metadata, or validation logic.
- Regex patterns and output structure can be adapted as orchestration needs evolve.
- Follows Elixir idioms for maintainability and contributor onboarding.

---

### `apps/engine/lib/workflow_parser_cfg.ex`

**Purpose:**
- Implements a NimbleParsec-based parser for strict validation of the LLM workflow DSL.
- Parses workflow definitions with nodes (id, op, optional depends_on, params) and edges, enabling robust and extensible workflow ingestion.

**Key Features:**
- **NimbleParsec Parsing:** Uses composable parser combinators for precise, maintainable, and extensible workflow parsing.
- **Strict Validation:** Enforces structure for nodes and edges, catching malformed or ambiguous workflow definitions early.
- **Parameter Extraction:** Supports parsing of key-value parameters, quoted strings, and numbers for node customization.
- **Reducer Functions:** Builds Elixir map structures from parsed AST for downstream engine consumption.

**Integration Points:**
- Used as a stricter alternative to regex-based parsing (see `WorkflowParser`) for workflows requiring validation or richer metadata.
- Compatible with the execution engine (XCS) and orchestration components.

**Extensibility Notes:**
- Easily extended to support additional node/edge attributes, richer DSL constructs, or custom validation rules.
- Modular parser design enables safe adaptation to evolving workflow DSLs.
- Follows Elixir idioms for maintainability and contributor onboarding.

---

### `lib/a2a_agent_web_web/operators/llm_operator.ex`

**Purpose:**
- Implements the LLMOperator, responsible for executing language model prompts using the OpenAI API.
- Provides a composable operator for LLM-based tasks in workflow graphs and orchestration.

**Key Features:**
- **Orchestrator Integration:** Implements the `call/1` entrypoint for orchestration compatibility, delegating to `run/2`.
- **Prompt Formatting:** Dynamically formats user-supplied prompt templates with context values.
- **LLM API Integration:** Sends requests to OpenAI GPT-4o, handles API responses, parses and returns results or errors.
- **Robust Logging:** Logs prompts, responses, and errors for observability and debugging.
- **Secure API Key Handling:** Reads the OpenAI API key from the environment variable; never hardcodes secrets.

**Integration Points:**
- Used as a node/operator in workflow graphs, invoked by the execution engine (XCS) and controllers.
- Composable with other operators and agents for complex workflows.

**Extensibility Notes:**
- Easily extended to support other LLM providers, prompt strategies, or output formats.
- Logging and error handling can be adapted for new requirements.
- Follows Elixir idioms for maintainability and contributor onboarding.

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

## Mix Generators

### Operator Generator: `mix a2a.gen.operator`

The A2A Agent Web app includes a Mix generator to streamline the creation of new operator modules and their corresponding test files.

**Usage:**

```sh
mix a2a.gen.operator MyNewOperator
```

This command will:
- Create a new operator module at `lib/a2a_agent_web_web/operators/my_new_operator.ex` with a starter structure and documentation.
- Automatically create a matching test file at `test/a2a_agent_web_web/operators/my_new_operator_test.exs` following ExUnit conventions.

**Features:**
- Ensures the operator module follows project conventions and implements the Operator protocol.
- Provides a docstring and a basic implementation for quick onboarding.
- The generated test file includes a starter test case to verify the operator's functionality.

**Example:**

```sh
mix a2a.gen.operator ExampleOperator
```

This will generate:
- `lib/a2a_agent_web_web/operators/example_operator.ex`
- `test/a2a_agent_web_web/operators/example_operator_test.exs`

Refer to the generated files for further customization and implementation details.

---

### Workflow Generator: `mix a2a.gen.workflow`

The project also provides a Mix generator to create new workflow YAML files based on a starter template.

**Usage:**

```sh
mix a2a.gen.workflow my_workflow
```

This command will:
- Create a new workflow YAML file at `workflows/my_workflow.yaml` with a starter structure and helpful comments.

**Features:**
- Provides a commented template with sample nodes, edges, and parameters.
- Ensures consistent structure for new workflows.

**Example:**

```sh
mix a2a.gen.workflow summarize_and_analyze
```

This will generate:
- `workflows/summarize_and_analyze.yaml`

Refer to the generated YAML file for further customization and implementation details.


## Architecture
- Integrates with the core agent and orchestrator apps
- Implements workflow execution, event streaming (NATS), and observability
- See the main [README](../../README.md) for full architecture
