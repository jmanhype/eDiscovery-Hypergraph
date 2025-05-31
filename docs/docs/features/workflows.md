---
id: workflows
title: Workflows
sidebar_label: Workflows
---

# Workflows

The eDiscovery Hypergraph platform provides a powerful workflow engine that allows you to create, customize, and automate complex document processing pipelines. Build workflows that combine AI analysis, human review, and business logic.

## Workflow Concepts

### Core Components

```yaml
# Example workflow structure
name: "Legal Document Review"
version: "1.0"
description: "Automated review pipeline for legal documents"

# Input schema validation
input_schema:
  type: object
  required: [documents, case_id]
  properties:
    documents:
      type: array
      items:
        type: string
    case_id:
      type: string

# Workflow nodes (operators)
nodes:
  - id: validate_input
    type: ValidationOperator
    config:
      schema: $input_schema
      
  - id: extract_text
    type: TextExtractionOperator
    depends_on: [validate_input]
    
  - id: classify_privilege
    type: PrivilegeClassificationOperator
    depends_on: [extract_text]
    
  - id: human_review
    type: HumanReviewOperator
    depends_on: [classify_privilege]
    when: "output.classify_privilege.confidence < 0.8"
    
  - id: final_processing
    type: AggregationOperator
    depends_on: [classify_privilege, human_review]

# Output configuration
output:
  format: "structured"
  include: [classifications, entities, summary]
```

## Creating Workflows

### 1. Workflow Builder UI

```typescript
export const WorkflowBuilder: React.FC = () => {
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [edges, setEdges] = useState<WorkflowEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  
  // Drag and drop handlers
  const onDrop = useCallback((event: DragEvent) => {
    event.preventDefault();
    const operatorType = event.dataTransfer?.getData("operator");
    
    if (operatorType) {
      const newNode: WorkflowNode = {
        id: generateId(),
        type: operatorType,
        position: { x: event.clientX, y: event.clientY },
        data: getDefaultConfig(operatorType)
      };
      
      setNodes([...nodes, newNode]);
    }
  }, [nodes]);
  
  // Connection handler
  const onConnect = useCallback((connection: Connection) => {
    const newEdge: WorkflowEdge = {
      id: generateId(),
      source: connection.source!,
      target: connection.target!,
      type: connection.type || "default"
    };
    
    // Validate connection
    if (validateConnection(nodes, newEdge)) {
      setEdges([...edges, newEdge]);
    }
  }, [nodes, edges]);
  
  return (
    <Box sx={{ height: "100vh", display: "flex" }}>
      {/* Operator palette */}
      <OperatorPalette />
      
      {/* Canvas */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onNodeClick={(_, node) => setSelectedNode(node)}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
      
      {/* Configuration panel */}
      {selectedNode && (
        <ConfigurationPanel
          node={selectedNode}
          onUpdate={(config) => updateNodeConfig(selectedNode.id, config)}
        />
      )}
    </Box>
  );
};
```

### 2. YAML Definition

```yaml
# workflows/ediscovery_advanced.yaml
name: "Advanced eDiscovery Pipeline"
version: "2.0"
tags: ["legal", "ai", "production"]

parameters:
  batch_size:
    type: integer
    default: 100
    description: "Number of documents to process in parallel"
  
  confidence_threshold:
    type: float
    default: 0.85
    description: "Minimum confidence for automated decisions"

nodes:
  # Input validation
  - id: input_validation
    operator: ValidateInputOperator
    config:
      required_fields: ["documents", "case_id", "client_id"]
      
  # Parallel document processing
  - id: process_batch
    operator: ParallelOperator
    depends_on: [input_validation]
    config:
      batch_size: ${parameters.batch_size}
      operators:
        - TextExtractionOperator
        - LanguageDetectionOperator
        - FormatNormalizationOperator
  
  # AI Analysis Branch
  - id: ai_analysis
    operator: BranchOperator
    depends_on: [process_batch]
    config:
      branches:
        - condition: "document.language == 'en'"
          operator: EnglishAnalysisOperator
        - condition: "document.language == 'es'"
          operator: SpanishAnalysisOperator
        - default: true
          operator: TranslateAndAnalyzeOperator
  
  # Quality check
  - id: quality_check
    operator: QualityAssuranceOperator
    depends_on: [ai_analysis]
    config:
      checks:
        - type: "completeness"
          required_fields: ["entities", "summary", "classification"]
        - type: "confidence"
          min_threshold: ${parameters.confidence_threshold}
  
  # Conditional human review
  - id: human_review_gate
    operator: ConditionalOperator
    depends_on: [quality_check]
    config:
      condition: |
        output.quality_check.passed == false ||
        output.ai_analysis.requires_review == true
      true_branch: human_review
      false_branch: auto_approve
  
  - id: human_review
    operator: HumanReviewOperator
    config:
      assignment_strategy: "round_robin"
      sla_hours: 24
      
  - id: auto_approve
    operator: AutoApprovalOperator
    config:
      add_metadata:
        approved_by: "system"
        approval_basis: "high_confidence"
  
  # Final aggregation
  - id: final_output
    operator: OutputFormatterOperator
    depends_on: [human_review, auto_approve]
    config:
      format: "legal_report"
      include_confidence_scores: true
      generate_summary: true

error_handling:
  on_error: "retry"
  max_retries: 3
  retry_delay: "exponential"
  fallback_workflow: "simple_processing"

monitoring:
  metrics:
    - "processing_time"
    - "error_rate"
    - "confidence_scores"
  alerts:
    - type: "threshold"
      metric: "error_rate"
      condition: "> 0.05"
      notify: ["ops-team@example.com"]
```

### 3. Programmatic Creation

```elixir
defmodule WorkflowFactory do
  @moduledoc """
  Factory for creating workflows programmatically
  """
  
  def create_dynamic_workflow(case_type, options \\ %{}) do
    %Workflow{
      name: "Dynamic #{case_type} Workflow",
      nodes: build_nodes_for_case_type(case_type, options),
      edges: build_edges_for_case_type(case_type),
      config: build_config(options)
    }
  end
  
  defp build_nodes_for_case_type(:litigation, options) do
    base_nodes = [
      %Node{
        id: "extract",
        operator: "TextExtractionOperator",
        config: %{method: "advanced_ocr"}
      },
      %Node{
        id: "privilege",
        operator: "PrivilegeDetectionOperator",
        config: %{
          model: "legal-bert-v2",
          threshold: options[:privilege_threshold] || 0.9
        }
      }
    ]
    
    # Add optional nodes based on options
    optional_nodes = []
    
    if options[:include_translation] do
      optional_nodes ++ [
        %Node{
          id: "translate",
          operator: "TranslationOperator",
          config: %{target_language: "en"}
        }
      ]
    end
    
    base_nodes ++ optional_nodes
  end
  
  def create_from_template(template_name, customizations \\ %{}) do
    template = Templates.get(template_name)
    
    workflow = %Workflow{
      name: "#{template.name} - Customized",
      base_template: template_name,
      nodes: template.nodes,
      edges: template.edges
    }
    
    # Apply customizations
    workflow
    |> customize_operators(customizations[:operators] || %{})
    |> add_custom_nodes(customizations[:additional_nodes] || [])
    |> update_parameters(customizations[:parameters] || %{})
  end
end
```

## Built-in Operators

### 1. Document Processing Operators

```python
class TextExtractionOperator(BaseOperator):
    """Extract text from various document formats"""
    
    async def execute(self, input_data: Dict) -> Dict:
        document = input_data["document"]
        
        # Detect format
        format_type = self.detect_format(document)
        
        # Extract based on format
        if format_type == "pdf":
            text = await self.extract_from_pdf(document)
        elif format_type == "docx":
            text = await self.extract_from_docx(document)
        elif format_type == "email":
            text = await self.extract_from_email(document)
        else:
            text = await self.extract_with_ocr(document)
        
        # Post-processing
        cleaned_text = self.clean_extracted_text(text)
        metadata = self.extract_metadata(document)
        
        return {
            "text": cleaned_text,
            "metadata": metadata,
            "format": format_type,
            "extraction_method": self.method_used,
            "confidence": self.calculate_extraction_confidence()
        }

class EntityExtractionOperator(BaseOperator):
    """Extract named entities using NER"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.nlp = spacy.load(config.get("model", "en_core_web_lg"))
        self.custom_patterns = self.load_custom_patterns()
    
    async def execute(self, input_data: Dict) -> Dict:
        text = input_data["text"]
        
        # Standard NER
        doc = self.nlp(text)
        entities = [
            {
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": self.get_confidence(ent)
            }
            for ent in doc.ents
        ]
        
        # Custom pattern matching
        custom_entities = self.match_custom_patterns(text)
        
        # Merge and deduplicate
        all_entities = self.merge_entities(entities, custom_entities)
        
        # Entity resolution
        resolved_entities = await self.resolve_entities(all_entities)
        
        return {
            "entities": resolved_entities,
            "entity_count": len(resolved_entities),
            "entity_types": self.count_by_type(resolved_entities)
        }
```

### 2. Control Flow Operators

```elixir
defmodule Operators.ConditionalOperator do
  @behaviour Operator
  
  @impl true
  def execute(input, config) do
    # Evaluate condition
    condition_result = evaluate_condition(config.condition, input)
    
    # Execute appropriate branch
    next_operator = if condition_result do
      config.true_branch
    else
      config.false_branch || config.default_branch
    end
    
    # Run the selected operator
    operator_module = Operators.get(next_operator)
    result = operator_module.execute(input, config.branch_configs[next_operator])
    
    # Add branching metadata
    {:ok, Map.put(result, :_branch_taken, next_operator)}
  end
  
  defp evaluate_condition(condition, context) do
    # Safe condition evaluation
    case Conditions.evaluate(condition, context) do
      {:ok, result} -> result
      {:error, _} -> false  # Default to false branch on error
    end
  end
end

defmodule Operators.LoopOperator do
  @behaviour Operator
  
  @impl true
  def execute(input, config) do
    # Initialize loop state
    state = %{
      items: get_items(input, config.items_path),
      results: [],
      iteration: 0
    }
    
    # Execute loop
    final_state = Enum.reduce_while(state.items, state, fn item, acc ->
      if acc.iteration >= config.max_iterations do
        {:halt, acc}
      else
        # Execute loop body
        case execute_iteration(item, acc, config) do
          {:ok, result} ->
            {:cont, %{acc | 
              results: [result | acc.results],
              iteration: acc.iteration + 1
            }}
          {:error, _} = error ->
            handle_loop_error(error, acc, config)
        end
      end
    end)
    
    {:ok, %{
      results: Enum.reverse(final_state.results),
      total_iterations: final_state.iteration
    }}
  end
end
```

### 3. Integration Operators

```python
class ExternalAPIOperator(BaseOperator):
    """Call external APIs within workflows"""
    
    async def execute(self, input_data: Dict) -> Dict:
        # Configure request
        request_config = self.build_request(input_data)
        
        # Add authentication
        headers = self.add_auth_headers(request_config.get("headers", {}))
        
        # Make request with retries
        async with aiohttp.ClientSession() as session:
            for attempt in range(self.config.get("max_retries", 3)):
                try:
                    async with session.request(
                        method=request_config["method"],
                        url=request_config["url"],
                        headers=headers,
                        json=request_config.get("body"),
                        timeout=self.config.get("timeout", 30)
                    ) as response:
                        
                        # Handle response
                        if response.status == 200:
                            data = await response.json()
                            return self.transform_response(data)
                        else:
                            if attempt < self.config.get("max_retries", 3) - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            else:
                                raise APIError(f"API returned {response.status}")
                                
                except Exception as e:
                    if attempt == self.config.get("max_retries", 3) - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)

class DatabaseOperator(BaseOperator):
    """Interact with databases in workflows"""
    
    async def execute(self, input_data: Dict) -> Dict:
        operation = self.config["operation"]
        
        if operation == "query":
            return await self.execute_query(input_data)
        elif operation == "insert":
            return await self.execute_insert(input_data)
        elif operation == "update":
            return await self.execute_update(input_data)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def execute_query(self, input_data: Dict) -> Dict:
        query = self.build_query(input_data)
        
        async with self.get_connection() as conn:
            results = await conn.fetch(query)
            
        return {
            "records": [dict(r) for r in results],
            "count": len(results),
            "query": query if self.config.get("include_query") else None
        }
```

## Advanced Features

### 1. Dynamic Workflows

```elixir
defmodule DynamicWorkflow do
  @doc """
  Workflows that adapt based on runtime conditions
  """
  
  def create_adaptive_workflow(initial_input) do
    # Analyze input to determine workflow structure
    analysis = analyze_input(initial_input)
    
    # Build workflow dynamically
    workflow = %Workflow{
      name: "Adaptive Workflow #{DateTime.utc_now()}",
      nodes: [],
      edges: []
    }
    
    # Add nodes based on analysis
    workflow = 
      workflow
      |> maybe_add_translation_node(analysis)
      |> maybe_add_ocr_node(analysis)
      |> add_core_processing_nodes(analysis)
      |> maybe_add_quality_checks(analysis)
    
    # Connect nodes
    workflow = connect_nodes(workflow)
    
    {:ok, workflow}
  end
  
  defp maybe_add_translation_node(workflow, %{languages: langs}) when length(langs) > 1 do
    add_node(workflow, %Node{
      id: "translate",
      operator: "TranslationOperator",
      config: %{
        target_language: "en",
        source_languages: langs
      }
    })
  end
  defp maybe_add_translation_node(workflow, _), do: workflow
end
```

### 2. Workflow Composition

```python
class WorkflowComposer:
    """Compose complex workflows from smaller sub-workflows"""
    
    def compose(self, workflows: List[Workflow]) -> Workflow:
        composed = Workflow(name="Composed Workflow")
        
        # Merge nodes with unique IDs
        node_mapping = {}
        for workflow in workflows:
            for node in workflow.nodes:
                new_id = f"{workflow.id}_{node.id}"
                node_mapping[node.id] = new_id
                composed.add_node(node.copy(id=new_id))
        
        # Update edges
        for workflow in workflows:
            for edge in workflow.edges:
                composed.add_edge(
                    source=node_mapping[edge.source],
                    target=node_mapping[edge.target]
                )
        
        # Add inter-workflow connections
        self.connect_workflows(composed, workflows)
        
        return composed
    
    def create_sub_workflow(
        self,
        parent_workflow: Workflow,
        nodes: List[str]
    ) -> Workflow:
        """Extract sub-workflow from parent"""
        
        sub_workflow = Workflow(name=f"Sub-workflow of {parent_workflow.name}")
        
        # Copy selected nodes
        for node_id in nodes:
            node = parent_workflow.get_node(node_id)
            sub_workflow.add_node(node.copy())
        
        # Copy relevant edges
        for edge in parent_workflow.edges:
            if edge.source in nodes and edge.target in nodes:
                sub_workflow.add_edge(edge.copy())
        
        # Add input/output interfaces
        self.add_interfaces(sub_workflow, parent_workflow, nodes)
        
        return sub_workflow
```

### 3. Workflow Versioning

```elixir
defmodule WorkflowVersioning do
  @moduledoc """
  Version control for workflows
  """
  
  def create_version(workflow, changes \\ %{}) do
    current_version = get_current_version(workflow)
    
    new_version = %WorkflowVersion{
      workflow_id: workflow.id,
      version_number: increment_version(current_version),
      changes: changes,
      created_by: get_current_user(),
      created_at: DateTime.utc_now(),
      parent_version: current_version.id,
      workflow_snapshot: serialize_workflow(workflow)
    }
    
    # Store version
    Repo.insert!(new_version)
    
    # Update workflow
    workflow
    |> Workflow.changeset(%{current_version: new_version.version_number})
    |> Repo.update!()
    
    {:ok, new_version}
  end
  
  def rollback(workflow, target_version) do
    version = get_version(workflow, target_version)
    
    # Restore workflow state
    restored_workflow = deserialize_workflow(version.workflow_snapshot)
    
    # Create rollback version
    create_version(restored_workflow, %{
      type: :rollback,
      from_version: workflow.current_version,
      to_version: target_version,
      reason: get_rollback_reason()
    })
  end
  
  def diff_versions(workflow, version1, version2) do
    v1 = get_version(workflow, version1)
    v2 = get_version(workflow, version2)
    
    %{
      nodes: diff_nodes(v1.workflow_snapshot, v2.workflow_snapshot),
      edges: diff_edges(v1.workflow_snapshot, v2.workflow_snapshot),
      config: diff_config(v1.workflow_snapshot, v2.workflow_snapshot)
    }
  end
end
```

## Workflow Execution

### 1. Execution Engine

```elixir
defmodule WorkflowEngine do
  use GenServer
  
  def execute(workflow, input, options \\ %{}) do
    # Create execution context
    context = %ExecutionContext{
      workflow_id: workflow.id,
      execution_id: UUID.generate(),
      input: input,
      options: options,
      started_at: DateTime.utc_now(),
      state: :running,
      results: %{},
      metadata: %{}
    }
    
    # Start execution
    GenServer.call(__MODULE__, {:execute, workflow, context})
  end
  
  def handle_call({:execute, workflow, context}, _from, state) do
    # Build execution graph
    graph = build_execution_graph(workflow)
    
    # Topological sort
    sorted_nodes = topological_sort(graph)
    
    # Execute nodes
    result = execute_nodes(sorted_nodes, context, workflow)
    
    # Record execution
    record_execution(context, result)
    
    {:reply, result, state}
  end
  
  defp execute_nodes(nodes, context, workflow) do
    Enum.reduce_while(nodes, {:ok, context}, fn node, {:ok, ctx} ->
      case execute_node(node, ctx, workflow) do
        {:ok, updated_ctx} ->
          {:cont, {:ok, updated_ctx}}
          
        {:error, error} ->
          handle_node_error(node, error, ctx, workflow)
          
        {:skip, reason} ->
          {:cont, {:ok, mark_skipped(ctx, node, reason)}}
      end
    end)
  end
  
  defp execute_node(node, context, workflow) do
    # Check conditions
    if should_execute?(node, context) do
      # Get operator
      operator = get_operator(node.operator)
      
      # Prepare input
      node_input = prepare_node_input(node, context)
      
      # Execute with monitoring
      with_monitoring(node, context) do
        operator.execute(node_input, node.config)
      end
    else
      {:skip, :condition_not_met}
    end
  end
end
```

### 2. Monitoring & Observability

```python
class WorkflowMonitor:
    def __init__(self):
        self.metrics = WorkflowMetrics()
        self.tracer = WorkflowTracer()
        
    async def monitor_execution(
        self,
        workflow: Workflow,
        execution_id: str
    ):
        """Monitor workflow execution in real-time"""
        
        # Start monitoring
        monitor_task = asyncio.create_task(
            self._monitor_loop(workflow, execution_id)
        )
        
        try:
            # Track metrics
            with self.metrics.track_execution(workflow.id):
                yield
        finally:
            monitor_task.cancel()
    
    async def _monitor_loop(self, workflow: Workflow, execution_id: str):
        while True:
            # Get execution state
            state = await self.get_execution_state(execution_id)
            
            # Update metrics
            self.metrics.update({
                "workflow_id": workflow.id,
                "execution_id": execution_id,
                "status": state.status,
                "nodes_completed": state.nodes_completed,
                "nodes_total": len(workflow.nodes),
                "duration": state.elapsed_time
            })
            
            # Check for issues
            if state.has_errors:
                await self.alert_on_errors(state.errors)
            
            if state.is_stuck:
                await self.alert_on_stuck_execution(state)
            
            # Broadcast updates
            await self.broadcast_status(state)
            
            await asyncio.sleep(1)
```

### 3. Error Handling & Recovery

```elixir
defmodule WorkflowErrorHandler do
  @moduledoc """
  Sophisticated error handling for workflows
  """
  
  def handle_error(error, node, context, options \\ %{}) do
    error_context = build_error_context(error, node, context)
    
    # Determine strategy
    strategy = determine_error_strategy(error_context, options)
    
    case strategy do
      :retry ->
        retry_node(node, context, options)
        
      :skip ->
        skip_node(node, context, error_context)
        
      :fail ->
        fail_workflow(context, error_context)
        
      :compensate ->
        run_compensation(node, context, error_context)
        
      :fallback ->
        run_fallback_workflow(context, options.fallback_workflow)
    end
  end
  
  defp retry_node(node, context, options) do
    retry_options = %{
      max_attempts: options[:max_retries] || 3,
      backoff: options[:retry_backoff] || :exponential,
      delay: options[:retry_delay] || 1000
    }
    
    Retry.retry_with_backoff(retry_options) do
      execute_node(node, context)
    end
  end
  
  defp run_compensation(node, context, error_context) do
    # Find compensation actions
    compensation_nodes = find_compensation_nodes(node, context.workflow)
    
    # Execute in reverse order
    compensation_nodes
    |> Enum.reverse()
    |> Enum.each(fn comp_node ->
      execute_compensation(comp_node, context, error_context)
    end)
    
    {:compensated, error_context}
  end
end
```

## Best Practices

### 1. Workflow Design

- **Modular Design**: Create reusable sub-workflows
- **Error Handling**: Always define error strategies
- **Idempotency**: Ensure operators are idempotent
- **Monitoring**: Add comprehensive logging and metrics

### 2. Performance Optimization

```python
# Parallel execution
class ParallelExecutor:
    async def execute_parallel(
        self,
        nodes: List[Node],
        context: ExecutionContext
    ):
        # Group independent nodes
        parallel_groups = self.identify_parallel_groups(nodes)
        
        results = {}
        for group in parallel_groups:
            # Execute group in parallel
            group_results = await asyncio.gather(*[
                self.execute_node(node, context)
                for node in group
            ])
            
            # Merge results
            for node, result in zip(group, group_results):
                results[node.id] = result
        
        return results
```

### 3. Testing Workflows

```elixir
defmodule WorkflowTest do
  use ExUnit.Case
  
  describe "workflow execution" do
    test "executes simple workflow successfully" do
      workflow = WorkflowFactory.create(:simple_extraction)
      input = %{document: "test document content"}
      
      assert {:ok, result} = WorkflowEngine.execute(workflow, input)
      assert result.extracted_text == "test document content"
    end
    
    test "handles errors gracefully" do
      workflow = WorkflowFactory.create(:with_failing_node)
      input = %{document: "test"}
      
      assert {:error, error} = WorkflowEngine.execute(workflow, input)
      assert error.recovered_by == :compensation
    end
    
    test "respects conditional execution" do
      workflow = WorkflowFactory.create(:conditional_workflow)
      
      # Test true branch
      input = %{value: 100}
      assert {:ok, result} = WorkflowEngine.execute(workflow, input)
      assert result.branch_taken == :high_value
      
      # Test false branch
      input = %{value: 10}
      assert {:ok, result} = WorkflowEngine.execute(workflow, input)
      assert result.branch_taken == :low_value
    end
  end
end
```

## Next Steps

- Review [API Documentation](/api/rest-api) for workflow endpoints
- Check [Examples](/examples) for real-world workflows
- Learn about [Deployment](/deployment/production-deployment) considerations
- Explore [Support](/support) resources