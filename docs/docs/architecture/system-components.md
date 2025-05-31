---
id: system-components
title: System Components
sidebar_label: System Components
---

# System Components

This page provides detailed information about each major component in the eDiscovery Hypergraph platform, their responsibilities, and how they interact.

## Phoenix/Elixir Backend

### Overview

The Phoenix backend serves as the primary API gateway and workflow orchestrator, leveraging Elixir's Actor model for massive concurrency and fault tolerance.

### Core Modules

#### 1. Endpoint Configuration

```elixir
defmodule A2AAgentWeb.Endpoint do
  use Phoenix.Endpoint, otp_app: :a2a_agent_web
  
  # WebSocket support for real-time updates
  socket "/socket", A2AAgentWeb.UserSocket,
    websocket: true,
    longpoll: false
  
  # GraphQL endpoint
  plug Absinthe.Plug.GraphiQL,
    schema: A2AAgentWeb.GraphQL.Schema,
    interface: :advanced
  
  # REST API routes
  plug A2AAgentWeb.Router
end
```

#### 2. Agent Registry

```elixir
defmodule A2AAgentWeb.AgentRegistry do
  use GenServer
  
  @doc """
  Registry for distributed agent discovery and health monitoring
  """
  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end
  
  def register_agent(agent_id, capabilities, metadata) do
    GenServer.call(__MODULE__, {:register, agent_id, capabilities, metadata})
  end
  
  def discover_agents(capability) do
    GenServer.call(__MODULE__, {:discover, capability})
  end
  
  # Callbacks
  def handle_call({:register, agent_id, capabilities, metadata}, _from, state) do
    agent = %{
      id: agent_id,
      capabilities: capabilities,
      metadata: metadata,
      status: :active,
      last_heartbeat: DateTime.utc_now()
    }
    
    new_state = Map.put(state.agents, agent_id, agent)
    Phoenix.PubSub.broadcast(state.pubsub, "agents:registered", {:agent_registered, agent})
    
    {:reply, :ok, %{state | agents: new_state}}
  end
end
```

#### 3. Workflow Engine

```elixir
defmodule A2AAgentWeb.WorkflowRunner do
  @moduledoc """
  Executes workflows with operator DAG resolution
  """
  
  def run(workflow, input) do
    with {:ok, dag} <- build_dag(workflow),
         {:ok, sorted_nodes} <- topological_sort(dag),
         {:ok, result} <- execute_nodes(sorted_nodes, input) do
      {:ok, result}
    end
  end
  
  defp execute_nodes(nodes, initial_input) do
    Enum.reduce_while(nodes, {:ok, initial_input}, fn node, {:ok, acc} ->
      case execute_operator(node, acc) do
        {:ok, result} -> {:cont, {:ok, merge_results(acc, result)}}
        {:error, _} = error -> {:halt, error}
      end
    end)
  end
end
```

### Key Features

- **Fault Tolerance**: Supervisor trees ensure system resilience
- **Hot Code Reloading**: Update code without downtime
- **Distributed Processing**: Seamlessly scale across nodes
- **Real-time Communication**: Phoenix Channels for WebSocket support

## Python AI Service

### Overview

The Python service handles all AI-related processing, integrating with OpenAI and custom NLP models.

### Architecture

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio
from typing import List, Dict, Any

app = FastAPI(title="eDiscovery AI Service")

class DocumentProcessor:
    """Main document processing pipeline"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.entity_extractor = EntityExtractor()
        self.classifier = PrivilegeClassifier()
        self.summarizer = DocumentSummarizer()
    
    async def process_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process document through AI pipeline"""
        
        # Parallel processing of different analyses
        tasks = [
            self.extract_entities(document),
            self.classify_privilege(document),
            self.generate_summary(document),
            self.analyze_sentiment(document)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            "entities": results[0],
            "privilege": results[1],
            "summary": results[2],
            "sentiment": results[3],
            "metadata": self.extract_metadata(document)
        }
```

### Key Services

#### 1. Entity Extraction

```python
class EntityExtractor:
    """Extract named entities using spaCy and OpenAI"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.custom_patterns = self.load_legal_patterns()
    
    async def extract(self, text: str) -> List[Entity]:
        # Use spaCy for initial extraction
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": self.calculate_confidence(ent)
            })
        
        # Enhance with OpenAI for context-aware extraction
        enhanced = await self.enhance_with_gpt(text, entities)
        
        return self.merge_and_deduplicate(entities, enhanced)
```

#### 2. Privilege Classification

```python
class PrivilegeClassifier:
    """Classify documents for legal privilege"""
    
    PRIVILEGE_TYPES = [
        "attorney_client",
        "work_product", 
        "executive_privilege",
        "trade_secret"
    ]
    
    async def classify(self, document: Dict[str, Any]) -> PrivilegeResult:
        # Extract features
        features = self.extract_features(document)
        
        # Use fine-tuned model for initial classification
        ml_prediction = self.ml_model.predict(features)
        
        # Validate with GPT-4 for complex cases
        if ml_prediction.confidence < 0.8:
            gpt_result = await self.verify_with_gpt(document)
            return self.combine_predictions(ml_prediction, gpt_result)
        
        return ml_prediction
```

### API Endpoints

```python
@app.post("/api/ediscovery/process")
async def process_document(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """Main document processing endpoint"""
    
    # Quick validation
    if not request.email:
        raise HTTPException(400, "Email content required")
    
    # Start processing
    processor = DocumentProcessor()
    result = await processor.process_document(request.dict())
    
    # Queue for hypergraph update
    background_tasks.add_task(update_hypergraph, result)
    
    return {
        "status": "success",
        "data": result,
        "processing_time": time.time() - start_time
    }
```

## React Frontend

### Overview

Modern React application providing intuitive UI for document management and analysis.

### Architecture

```typescript
// Core application structure
src/
├── components/          # Reusable UI components
│   ├── DocumentViewer/
│   ├── EntityGraph/
│   ├── SearchInterface/
│   └── WorkflowBuilder/
├── contexts/           # React contexts for state
├── hooks/              # Custom React hooks
├── pages/              # Page components
├── services/           # API integration
└── utils/              # Helper functions
```

### Key Components

#### 1. Document Processing Interface

```typescript
interface DocumentProcessorProps {
  caseId: string;
  onComplete: (results: ProcessingResult[]) => void;
}

export const DocumentProcessor: React.FC<DocumentProcessorProps> = ({
  caseId,
  onComplete
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState<ProcessingProgress>({});
  
  // WebSocket for real-time updates
  const { subscribe } = useWebSocket();
  
  useEffect(() => {
    const unsubscribe = subscribe(`processing.${caseId}`, (update) => {
      setProgress(prev => ({
        ...prev,
        [update.documentId]: update.progress
      }));
    });
    
    return unsubscribe;
  }, [caseId]);
  
  const handleUpload = async () => {
    setProcessing(true);
    
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('caseId', caseId);
    
    try {
      const response = await api.post('/documents/process', formData);
      onComplete(response.data.results);
    } finally {
      setProcessing(false);
    }
  };
  
  return (
    <Box>
      <FileUploader
        onFilesSelected={setFiles}
        accept=".pdf,.doc,.docx,.eml,.msg"
      />
      
      {Object.entries(progress).map(([docId, prog]) => (
        <ProgressBar
          key={docId}
          value={prog.percent}
          label={prog.status}
        />
      ))}
      
      <Button
        onClick={handleUpload}
        disabled={!files.length || processing}
        variant="contained"
      >
        Process Documents
      </Button>
    </Box>
  );
};
```

#### 2. Entity Relationship Visualization

```typescript
export const EntityGraph: React.FC<EntityGraphProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!data || !svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    const { nodes, links } = processHypergraphData(data);
    
    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));
    
    // Render nodes and edges
    const link = svg.selectAll(".link")
      .data(links)
      .enter().append("line")
      .attr("class", "link")
      .style("stroke", "#999")
      .style("stroke-width", d => Math.sqrt(d.weight));
    
    const node = svg.selectAll(".node")
      .data(nodes)
      .enter().append("g")
      .attr("class", "node")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));
    
    // Update positions on tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
      
      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });
  }, [data]);
  
  return <svg ref={svgRef} width={800} height={600} />;
};
```

### State Management

```typescript
// Using Redux Toolkit for complex state
export const documentSlice = createSlice({
  name: 'documents',
  initialState: {
    items: [],
    loading: false,
    filters: {},
    selectedIds: []
  },
  reducers: {
    setDocuments: (state, action) => {
      state.items = action.payload;
    },
    updateDocument: (state, action) => {
      const index = state.items.findIndex(d => d.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    }
  }
});
```

## Data Storage

### MongoDB Configuration

```javascript
// Document schema
const DocumentSchema = {
  _id: ObjectId,
  caseId: ObjectId,
  title: String,
  content: String,
  contentHash: String,
  metadata: {
    author: String,
    createdDate: Date,
    modifiedDate: Date,
    fileType: String,
    size: Number
  },
  processing: {
    status: String, // pending, processing, completed, failed
    startedAt: Date,
    completedAt: Date,
    results: {
      entities: Array,
      privilege: Object,
      summary: String,
      embeddings: Array
    }
  },
  hypergraph: {
    nodeId: String,
    connectedEdges: Array
  },
  audit: {
    createdBy: ObjectId,
    updatedBy: ObjectId,
    accessLog: Array
  }
};

// Indexes for performance
db.documents.createIndex({ caseId: 1, "processing.status": 1 });
db.documents.createIndex({ "metadata.createdDate": -1 });
db.documents.createIndex({ contentHash: 1 }, { unique: true });
db.documents.createIndex({ 
  "content": "text", 
  "metadata.author": "text", 
  "processing.results.summary": "text" 
});
```

### NATS Streaming

```elixir
defmodule EventStreaming do
  use GenServer
  
  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end
  
  def init(_opts) do
    {:ok, conn} = Gnat.start_link(%{host: "localhost", port: 4222})
    {:ok, %{conn: conn, subscriptions: %{}}}
  end
  
  def publish(subject, data) do
    GenServer.cast(__MODULE__, {:publish, subject, data})
  end
  
  def subscribe(subject, handler) do
    GenServer.call(__MODULE__, {:subscribe, subject, handler})
  end
  
  # Stream processing example
  def handle_cast({:publish, subject, data}, state) do
    Gnat.pub(state.conn, subject, Jason.encode!(data))
    {:noreply, state}
  end
end
```

## Monitoring & Observability

### Prometheus Integration

```elixir
defmodule Metrics do
  use Prometheus.PlugExporter
  
  def setup do
    # Counter for processed documents
    Counter.declare(
      name: :documents_processed_total,
      help: "Total number of documents processed",
      labels: [:case_id, :status]
    )
    
    # Histogram for processing time
    Histogram.declare(
      name: :document_processing_duration_seconds,
      help: "Document processing duration",
      buckets: [0.1, 0.5, 1, 5, 10, 30, 60],
      labels: [:operation]
    )
    
    # Gauge for active workflows
    Gauge.declare(
      name: :active_workflows,
      help: "Number of active workflows"
    )
  end
end
```

### Distributed Tracing

```elixir
defmodule Tracing do
  @tracer :opentelemetry.get_tracer(:a2a_agent_web)
  
  def trace_operation(name, attributes, fun) do
    OpenTelemetry.Tracer.with_span @tracer, name, %{attributes: attributes} do
      try do
        result = fun.()
        OpenTelemetry.Span.set_status(OpenTelemetry.status(:ok))
        result
      rescue
        e ->
          OpenTelemetry.Span.record_exception(e)
          OpenTelemetry.Span.set_status(OpenTelemetry.status(:error))
          reraise e, __STACKTRACE__
      end
    end
  end
end
```

## Security Components

### Authentication Service

```elixir
defmodule Auth do
  use Guardian, otp_app: :a2a_agent_web
  
  def subject_for_token(user, _claims) do
    {:ok, to_string(user.id)}
  end
  
  def resource_from_claims(%{"sub" => id}) do
    case Users.get_user(id) do
      nil -> {:error, :resource_not_found}
      user -> {:ok, user}
    end
  end
  
  def verify_permissions(user, required_permissions) do
    user_permissions = Users.get_permissions(user)
    
    required_permissions
    |> Enum.all?(&(&1 in user_permissions))
    |> case do
      true -> :ok
      false -> {:error, :insufficient_permissions}
    end
  end
end
```

## Next Steps

- Learn about [AI Analysis](/features/ai-analysis) capabilities
- Explore [Search](/features/search) functionality
- Understand [Workflows](/features/workflows)
- Review [API Documentation](/api/rest-api)