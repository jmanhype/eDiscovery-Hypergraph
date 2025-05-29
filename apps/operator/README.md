# Operator

This app implements the core operator library for the Ember-to-Elixir port. Operators are the building blocks for agent workflows and orchestration.

## Purpose
- Provides a protocol for defining computational units (operators)
- Implements core operators for LLM execution, mapping, sequencing, and parallelization
- Enables composition and extension of agentic workflows

## Operator Protocol
- **Operator**: A module that implements the `Operator` behaviour and transforms inputs to outputs
- **Specification Protocol**: Handles input/output validation (Specification Pattern)
- **Extensible**: Add new operators by implementing the protocol

## Core Operators
- **LLMOperator**: Executes a language model with a formatted prompt
- **MapOperator**: Applies a function to an input value and returns the result
- **SequenceOperator**: Executes a sequence of operators in order, passing outputs from one to the next
- **ParallelOperator**: Executes multiple operators in parallel and merges their outputs

## Example Usage
```elixir
# Define and run a sequence workflow
workflow = %{
  nodes: [
    %{id: :step1, op: :llm, params: %{prompt: "Summarize this..."}},
    %{id: :step2, op: :map, params: %{fn: &String.upcase/1}, depends_on: [:step1]}
  ],
  edges: [
    %{from: :step1, to: :step2}
  ]
}
Operator.run(workflow, input: %{text: "Long document..."})
```

## Adding a New Operator
1. Implement the `Operator` behaviour in a new module:
   ```elixir
   defmodule MyCustomOperator do
     @behaviour Operator
     def run(input, opts \\ []), do: ...
   end
   ```
2. Register and use it in your workflow graphs.

## Specification Protocol
- Use specifications to validate operator inputs and outputs
- See `lib/operator/specification/` for examples

## Related Docs
- [Engine App (XCS)](../engine/README.md)
- [Orchestrator App](../hypergraph_agent/README.md)
- [Umbrella README](../../a2a_agent_umbrella/README.md)

---

For architecture, usage, and API details, see the main [README](../../README.md).

