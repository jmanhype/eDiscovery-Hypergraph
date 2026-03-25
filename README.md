# eDiscovery-Hypergraph

Legal document analysis platform. Combines a FastAPI/Python backend, React/TypeScript frontend, and an Elixir-based hypergraph workflow engine for document processing pipelines.

## Status

Prototype. The Docker Compose file wires up 6 services (Elixir, Python, NATS, MongoDB, Elasticsearch, React) but there is no evidence of end-to-end integration testing. CI badge in the previous README pointed to a workflow file that may not exist. The "85% coverage" badge was hardcoded, not generated.

## What It Does

1. Ingests legal documents (email text, uploaded files)
2. Runs AI analysis via OpenAI GPT models to detect:
   - Attorney-client privilege
   - Work product privilege
   - Significant evidence
3. Extracts entities (people, organizations, dates, monetary amounts)
4. Generates legal-context summaries
5. Organizes results by case/matter with search and filtering

## Architecture

| Layer | Technology | Port |
|---|---|---|
| Frontend | React 18, TypeScript, Material-UI, Vite | 5173 |
| Backend API | FastAPI, Pydantic, Motor (async MongoDB) | 8000 |
| Workflow Engine | Elixir/Phoenix, hypergraph execution | 4000 |
| Document Store | MongoDB 7.0 | 27017 |
| Full-Text Search | Elasticsearch 8.11 | 9200 |
| Messaging | NATS 2.10 | 4222 |
| AI | OpenAI API (GPT models) | -- |

## Project Layout

```
frontend/               # React/TypeScript SPA
  src/
    components/         # Reusable UI components
    pages/              # Route pages
    api/                # API client layer
    types/              # TypeScript definitions
backend/                # FastAPI Python backend
  server.py             # API endpoints
  models.py             # Pydantic models
  crud.py               # MongoDB CRUD
  requirements.txt
a2a_agent_umbrella/     # Elixir umbrella app
  apps/
    a2a_agent/          # Core agent logic
    a2a_agent_web/      # Phoenix API + workflow operators
      workflows/        # YAML workflow definitions
      openapi.yaml
agents/
  python_agents/
    minimal_a2a_agent/  # Python agent for A2A protocol
docker-compose.yml      # 6-service stack
Makefile                # up, down, test, lint
```

## Setup

### Prerequisites

- Docker and Docker Compose (simplest path)
- Or individually: Elixir 1.15+, Python 3.11+, Node.js 18+, MongoDB, NATS

### Docker Compose (all services)

```bash
git clone https://github.com/jmanhype/eDiscovery-Hypergraph.git
cd eDiscovery-Hypergraph
cp .env.example .env
# Edit .env: set OPENAI_API_KEY
make up
```

### Manual Setup

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --port 8000 --reload

# Frontend
cd frontend
npm install && npm run dev

# Elixir engine
mix deps.get && mix phx.server
```

### Access Points

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Hypergraph API | http://localhost:4000 |

## API Endpoints

### Documents

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/documents` | Create document |
| GET | `/api/documents/{id}` | Get document |
| PUT | `/api/documents/{id}` | Update document |
| DELETE | `/api/documents/{id}` | Archive document |
| POST | `/api/documents/search` | Search with filters |
| GET | `/api/documents/{id}/entities` | Extracted entities |

### Cases

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/cases` | Create case |
| GET | `/api/cases/{id}` | Get case |
| GET | `/api/cases` | List cases |

### Processing

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/ediscovery/process` | Process document(s) through AI pipeline |

## Limitations

- The CI and coverage badges were decorative, not connected to real pipelines.
- OpenAI API key is required for all AI features; no fallback or local model option.
- The Elixir hypergraph engine and the Python backend are loosely coupled via NATS; failure modes between them are not documented.
- Elasticsearch and MongoDB both store document data, but the sync mechanism between them is unclear.
- No authentication or RBAC implementation despite the README previously claiming "role-based access control."
- The A2A (agent-to-agent) protocol implementation is minimal.
- The `.devcontainer` directory contains 4 different Dockerfiles suggesting environment setup has been unstable.

## License

MIT. See `LICENSE`.
