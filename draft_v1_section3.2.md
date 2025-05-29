# Hypergraph Agents Umbrella: A Multi-Language, High-Performance Agentic AI Framework

## 3. Key Features

### 3.2 Workflow Engine (XCS)

The Workflow Engine, often referred to as XCS (Execution Control System), is the computational heart of Hypergraph Agents. It provides a powerful framework for defining, managing, and executing complex computational workflows as directed graphs of operations.

#### Graph-Based Execution Model

The XCS engine represents workflows as directed graphs where:

- **Nodes**: Individual computational operations (implemented as operators)
- **Edges**: Data dependencies between operations

This representation enables several key capabilities:

```elixir
@type node_id :: any()
@type graph :: %{node_id() => %{operator: module(), deps: [node_id()]}}
@type input :: map()
@type output :: map()
```

The graph structure allows for natural expression of complex dependencies while enabling the engine to determine optimal execution strategies. Developers can define workflows using YAML, Elixir, or Python, with each node in the graph representing a discrete operation with explicit dependencies.

#### Topological Sorting and Dependency Resolution

A core function of the XCS engine is its ability to analyze workflow graphs and determine a valid execution order through topological sorting:

```elixir
@spec topo_sort(graph()) :: [node_id()]
def topo_sort(graph) do
  nodes = Map.keys(graph)
  visited = MapSet.new()
  Enum.reduce(nodes, {[], visited}, fn node, {acc, vis} ->
    visit(node, graph, acc, vis)
  end)
  |> elem(0)
  |> Enum.reverse()
end
```

This algorithm:

1. Identifies all nodes in the graph
2. Traverses the graph depth-first, respecting dependencies
3. Produces an ordered list where each node appears after all its dependencies

This approach ensures that operations only execute when their required inputs are available, preventing race conditions and ensuring deterministic results.

#### Sequential vs. Parallel Execution Modes

The XCS engine supports both sequential and parallel execution modes:

1. **Sequential Execution**: Operations are executed one after another in dependency order, maximizing simplicity and determinism.

2. **Parallel Execution**: Independent operations (those with no mutual dependencies) can be executed simultaneously, maximizing throughput:

```elixir
@spec exec_parallel(graph(), [node_id()], input()) :: %{node_id() => output()}
def exec_parallel(graph, order, input) do
  levels = group_by_level(graph, order)
  Enum.reduce(levels, %{}, fn level, acc ->
    tasks = for node <- level do
      Task.async(fn ->
        # Execute node operation
        {node, node_output}
      end)
    end
    results = Task.await_many(tasks)
    Enum.into(results, acc)
  end)
end
```

The engine intelligently groups operations by "levels" (nodes with the same dependency depth), enabling it to maximize parallelism while respecting dependencies.

#### YAML/Elixir/Python Workflow Definitions

A key strength of the XCS engine is its flexibility in workflow definition formats:

**YAML Definition**:
```yaml
nodes:
  - id: summarize
    op: LLMOperator
    params:
      prompt_template: "Summarize: ~s"
      context:
        topic: "Elixir DSLs"
    depends_on: []
  - id: analyze
    op: MapOperator
    params:
      function: null
    depends_on: [summarize]
edges:
  - "summarize->analyze"
```

**Elixir Definition**:
```elixir
defmodule MyWorkflow do
  def definition do
    %{
      nodes: [
        %{id: :summarize, op: LLMOperator, params: %{prompt: "Summarize"}},
        %{id: :analyze, op: MapOperator, depends_on: [:summarize]}
      ],
      edges: ["summarize->analyze"]
    }
  end
end
```

The workflow parser handles conversion from these representations to the internal graph structure, making the system accessible to users with different preferences and backgrounds.

The XCS engine combines graph theory, parallel computation, and flexible definition formats to create a powerful framework for orchestrating complex AI workflows, enabling developers to focus on what operations they need rather than how to coordinate them. 