# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hypergraph Agents Umbrella project extended with eDiscovery capabilities. It combines:
- **Base Framework**: Multi-language, distributed AI workflow framework (Elixir/Python)
- **eDiscovery Extension**: Legal document processing through AI pipeline for entity extraction, privilege classification, and summarization

## Starting Services

### Required Services
```bash
# Start MongoDB
brew services start mongodb-community

# Start NATS server
brew services start nats-server
# Or: nats-server

# Start Phoenix server with IEx
iex -S mix phx.server

# Start eDiscovery backend (with OpenAI API key)
cd backend && OPENAI_API_KEY=your_key_here python server.py
# Or: OPENAI_API_KEY=your_key_here uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## Common Commands

### Elixir/Umbrella Development
```bash
# Install dependencies
mix deps.get
mix deps.compile

# Start Phoenix server with IEx
iex -S mix phx.server

# Run tests
mix test

# Generate new operator
mix a2a.gen.operator MyOperator

# Run workflow
mix workflow.run workflows/my_workflow.yaml
```

### Python Agent Development  
```bash
# Install Python agent dependencies
cd agents/python_agents/minimal_a2a_agent
pip install -r requirements.txt

# Run Python agent
python app.py
```

### eDiscovery Backend Development
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Run tests
pytest
```

### Frontend Development
```bash
# Install dependencies
cd frontend && yarn install

# Start development server
yarn start

# Build for production
yarn build
```

### Docker Operations
```bash
# Build and run the full stack
docker build -t ediscovery-hypergraph .
docker run -p 8080:8080 -p 8001:8001 -p 4000:4000 ediscovery-hypergraph
```

## Architecture

### Hypergraph Framework Components

**Core Apps** (`apps/`)
- **a2a_agent_web**: Phoenix web app with A2A protocol, agent registry, workflow execution
- **engine**: Workflow execution engine with topological sorting
- **operator**: Base operators and operator protocol
- **hypergraph_agent**: Agent behavior definitions

**Agent Communication**
- **A2A Protocol**: JSON-based agent-to-agent messaging
- **NATS/PubSub**: Distributed event streaming
- **Agent Registry**: Service discovery via Phoenix.PubSub

### eDiscovery Extension

**Processing Flow**
1. **Email Input** → FastAPI endpoint (`/api/ediscovery/process`)
2. **AI Pipeline**:
   - Entity extraction (people, organizations, locations)
   - Privilege classification (attorney-client, work-product)
   - Content summarization
   - Evidence identification
3. **Output**: Structured legal analysis with knowledge graph data

**Key Components**
- **eDiscovery Backend** (`backend/server.py`): FastAPI with OpenAI integration
- **Frontend** (`frontend/src/`): React 19 with Tailwind CSS
- **Demo Interface** (`ediscovery_demo.html`): Quick testing UI

### Integration Points

**eDiscovery Operators** (in `apps/a2a_agent_web/lib/a2a_agent_web_web/operators/`)
- `EdiscoverySummarizationOperator` - Document summarization
- `EdiscoveryClassificationOperator` - Legal privilege classification  
- `EdiscoveryEntityExtractionOperator` - Entity extraction
- `EdiscoveryAggregationOperator` - Result aggregation

**NATS Subjects** (Future - currently using HTTP)
- `ediscovery.summarize` / `ediscovery.summarize.response`
- `ediscovery.classify` / `ediscovery.classify.response`
- `ediscovery.extract_entities` / `ediscovery.extract_entities.response`

**API Endpoints**
- **Phoenix**: `POST /api/a2a` - Agent communication
- **FastAPI**: `POST /api/ediscovery/process` - Document processing
- **Metrics**: `GET /metrics` - Prometheus metrics

### Service Dependencies
- **Required**: Elixir/OTP, Python 3.8+, NATS server, MongoDB
- **For AI features**: OpenAI API key (set as OPENAI_API_KEY environment variable)

## Creating eDiscovery Agents

To add eDiscovery agents to the umbrella:

1. **Create agent module** in `apps/a2a_agent_web/lib/a2a_agent_web_web/agents/`
2. **Define operators** in `apps/a2a_agent_web/lib/a2a_agent_web_web/operators/`
3. **Create workflows** in `apps/a2a_agent_web/workflows/`
4. **Register with AgentRegistry** for discovery

### eDiscovery Workflow

**Optimized Workflow** (`apps/a2a_agent_web/workflows/ediscovery_optimized.yaml`) - Recommended:
```yaml
name: "eDiscovery Optimized Processing"
nodes:
  - id: process  # Single API call to backend
    op: EdiscoveryProcessOperator
  - id: extract_summary  # Extract from cached result
    op: EdiscoveryExtractSummaryOperator
    depends_on: [process]
  - id: extract_classification  # Extract from cached result
    op: EdiscoveryExtractClassificationOperator
    depends_on: [process]
  - id: extract_entities  # Extract from cached result
    op: EdiscoveryExtractEntitiesOperator
    depends_on: [process]
  - id: aggregate_results
    op: EdiscoveryAggregationOperator
    depends_on: ["extract_summary", "extract_classification", "extract_entities"]
```

Run with:
```bash
# Optimized workflow (single backend call):
mix workflow.run apps/a2a_agent_web/workflows/ediscovery_optimized.yaml \
  --json '{"email":"Your legal document text here"}'

# Original workflow (3 parallel backend calls - for comparison):
mix workflow.run apps/a2a_agent_web/workflows/ediscovery_process.yaml \
  --json '{"email":"Your legal document text here"}'
```

The optimized workflow is 3x faster by making only one API call to the backend instead of three parallel calls.