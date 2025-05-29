# eDiscovery Hypergraph Platform

**Full-Stack Legal Document Analysis & eDiscovery Platform** powered by AI workflows and distributed hypergraph agents.

[![CI](https://img.shields.io/github/actions/workflow/status/jmanhype/eDiscovery-Hypergraph/ci.yml?style=flat-square)](https://github.com/jmanhype/eDiscovery-Hypergraph/actions)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen?style=flat-square)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🏛️ Overview

A comprehensive eDiscovery platform that combines the power of **Hypergraph Agents** distributed AI framework with specialized legal document processing capabilities. Built for law firms, legal departments, and compliance teams who need intelligent, scalable document analysis with full audit trails.

<p align="center">
  <img src="https://github.com/jmanhype/hypergraph_agents_umbrella/raw/main/2025-04-20%2013.29.32.jpg" alt="Keylon Partiki Pattern" width="350" />
</p>
<p align="center"><em>Keylon Partiki Pattern – Symbolizing distributed intelligence and interconnected legal workflows</em></p>

---

## 🚀 Key Features

### 🔍 **AI-Powered Document Analysis**
- **Automatic Privilege Detection**: Attorney-client, work product, confidential
- **Evidence Identification**: Flags documents with significant evidence
- **Entity Extraction**: People, organizations, locations, dates, monetary amounts
- **Smart Summarization**: Legal-context aware document summaries
- **Classification**: Automated document categorization and tagging

### 🏗️ **Full-Stack Architecture**
- **Frontend**: React + TypeScript + Material-UI
- **Backend**: FastAPI + Python with comprehensive CRUD operations
- **Workflow Engine**: Elixir-based hypergraph execution engine
- **Database**: MongoDB for document storage and metadata
- **Messaging**: NATS for distributed agent communication
- **AI Integration**: OpenAI GPT models with legal-specific prompts

### 📊 **Case & Matter Management**
- **Case Organization**: Structured case/matter hierarchy
- **Batch Processing**: Bulk document analysis workflows
- **User Management**: Role-based access control
- **Audit Trails**: Complete compliance logging
- **Deadline Tracking**: Review and production deadlines

### 🔄 **Distributed Workflow System**
- **Hypergraph Agents**: Multi-language AI agent framework
- **A2A Protocol**: Agent-to-agent communication
- **Parallel Processing**: Optimized document processing pipelines
- **Real-time Updates**: Live processing status and results
- **Scalable Architecture**: Handles enterprise document volumes

---

## 📁 Project Structure

```text
eDiscovery-Hypergraph/
├── frontend/                    # React TypeScript Frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Application pages
│   │   ├── api/               # API client layer
│   │   └── types/             # TypeScript definitions
│   └── package.json
├── backend/                     # FastAPI Python Backend
│   ├── models.py              # Pydantic data models
│   ├── crud.py                # Database operations
│   ├── server.py              # API endpoints
│   └── requirements.txt
├── apps/                        # Elixir Hypergraph Framework
│   ├── a2a_agent_web/         # Web API & operators
│   ├── engine/                # Workflow execution engine
│   └── operator/              # Base operator framework
├── agents/                      # Multi-language agents
│   └── python_agents/         # Python AI agents
└── workflows/                   # eDiscovery workflows
    ├── ediscovery_process.yaml
    └── ediscovery_optimized.yaml
```

---

## 🏃‍♂️ Quick Start

### Prerequisites
- **Elixir 1.15+** & **Erlang/OTP 26+**
- **Python 3.11+**
- **Node.js 18+**
- **MongoDB** (running locally or Docker)
- **NATS Server** (optional, for distributed processing)

### 1. **Clone & Setup**
```bash
git clone https://github.com/jmanhype/eDiscovery-Hypergraph.git
cd eDiscovery-Hypergraph

# Install Elixir dependencies
mix deps.get

# Setup Python backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup React frontend
cd ../frontend
npm install
```

### 2. **Configure Environment**
```bash
# Root .env file
export OPENAI_API_KEY="your-openai-api-key"
export MONGO_URL="mongodb://localhost:27017"
export NATS_URL="nats://localhost:4222"

# Backend .env
echo 'OPENAI_API_KEY=your-openai-api-key' > backend/.env
echo 'MONGO_URL=mongodb://localhost:27017' >> backend/.env

# Frontend .env
echo 'VITE_API_URL=http://localhost:8000' > frontend/.env
```

### 3. **Start Services**

**Terminal 1 - MongoDB:**
```bash
# macOS with Homebrew
brew services start mongodb-community

# Or with Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Terminal 2 - NATS (Optional):**
```bash
# Download and run NATS server
nats-server --port 4222
```

**Terminal 3 - Backend API:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn server:app --port 8000 --reload
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 5 - Hypergraph Engine:**
```bash
# Start Phoenix server for hypergraph workflows
mix phx.server
```

### 4. **Access the Platform**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Hypergraph API**: http://localhost:4000

---

## 🎯 Usage Examples

### 📝 **Process Legal Documents**

**Via Frontend:**
1. Navigate to http://localhost:5173
2. Go to "Processing" tab
3. Paste document content
4. Click "Process" to analyze

**Via API:**
```python
import requests

# Process a legal document
response = requests.post('http://localhost:8000/api/ediscovery/process', json={
    "emails": [{
        "subject": "Confidential Legal Matter",
        "body": "Dear Counsel, This communication is attorney-client privileged..."
    }]
})

print(response.json())
```

**Via Hypergraph Workflow:**
```bash
# Run optimized eDiscovery workflow
mix workflow.run apps/a2a_agent_web/workflows/ediscovery_optimized.yaml \
  --input '{"email_text":"Your document content here..."}'
```

### 🗂️ **Manage Cases & Documents**

**Create a Case:**
```python
import requests

case_data = {
    "name": "Smith vs. Jones Patent Dispute",
    "client_name": "Smith Industries",
    "matter_number": "SMITH-2024-001",
    "description": "Patent infringement litigation"
}

response = requests.post('http://localhost:8000/api/cases', json=case_data)
case = response.json()
print(f"Created case: {case['_id']}")
```

**Upload & Process Documents:**
```python
# Create document in case
doc_data = {
    "case_id": case['_id'],
    "title": "Key Patent Document",
    "content": "This document describes our proprietary technology...",
    "author": "Dr. Smith",
    "tags": ["patent", "technical", "confidential"]
}

response = requests.post('http://localhost:8000/api/documents', json=doc_data)
document = response.json()

# Document is automatically processed by AI in background
```

### 🔍 **Search & Filter Documents**

```python
# Search for privileged documents with evidence
search_params = {
    "case_id": case['_id'],
    "privilege_type": "attorney-client",
    "has_significant_evidence": True,
    "limit": 50
}

response = requests.post('http://localhost:8000/api/documents/search', json=search_params)
privileged_docs = response.json()

for doc in privileged_docs:
    print(f"🔒 {doc['title']} - {doc['privilege_type']}")
```

---

## 🧠 AI Analysis Capabilities

### **Privilege Detection**
The platform automatically identifies and classifies privileged communications:
- **Attorney-Client Privilege**: Communications between lawyers and clients
- **Work Product**: Legal strategy and case preparation materials
- **Confidential**: Sensitive business information

### **Evidence Identification**
AI models trained on legal contexts identify documents containing:
- **Factual Evidence**: Key facts relevant to legal matters
- **Smoking Gun Documents**: Critical evidence in litigation
- **Chain of Custody**: Document authenticity and handling

### **Entity Recognition**
Extracts and links legal entities:
- **People**: Witnesses, parties, attorneys, experts
- **Organizations**: Companies, law firms, government agencies
- **Locations**: Addresses, jurisdictions, incident locations
- **Dates**: Key event dates, deadlines, statutes of limitations
- **Financial**: Damages amounts, settlement figures, costs

### **Smart Summarization**
Legal-context aware summaries that preserve:
- **Key Legal Arguments**: Main points and legal theories
- **Factual Findings**: Important facts and evidence
- **Action Items**: Tasks, deadlines, and next steps
- **Risk Assessment**: Potential legal exposure and mitigation

---

## 🔧 API Reference

### **Core Endpoints**

#### **Documents**
- `POST /api/documents` - Create document
- `GET /api/documents/{id}` - Get document details
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Archive document
- `POST /api/documents/search` - Search documents
- `GET /api/documents/{id}/entities` - Get extracted entities

#### **Cases**
- `POST /api/cases` - Create new case
- `GET /api/cases/{id}` - Get case details
- `GET /api/cases` - List cases (with optional user filter)

#### **Processing**
- `POST /api/ediscovery/process` - Process documents through AI pipeline
- `POST /api/batches` - Create document processing batch
- `GET /api/batches/{id}` - Get batch status

#### **Entities**
- `GET /api/entities` - Search entities across documents
- `GET /api/entities/{id}/documents` - Get documents containing entity

#### **Workflows**
- `POST /api/workflows/start` - Start hypergraph workflow

### **Data Models**

**Document:**
```typescript
interface Document {
  _id?: string;
  case_id?: string;
  title: string;
  content: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  privilege_type?: 'none' | 'attorney-client' | 'work-product';
  has_significant_evidence: boolean;
  summary?: string;
  entities: Entity[];
  tags: string[];
  author?: string;
  created_at: string;
  updated_at: string;
}
```

**Case:**
```typescript
interface Case {
  _id?: string;
  name: string;
  client_name: string;
  matter_number: string;
  status: string;
  document_count: number;
  assigned_users: string[];
  review_deadline?: string;
  production_deadline?: string;
  created_at: string;
}
```

---

## 🔄 Workflow System

The platform uses **Hypergraph Agents** for distributed AI workflow execution:

### **Built-in Workflows**

#### **eDiscovery Process (ediscovery_process.yaml)**
Sequential processing pipeline:
1. **Document Processing** - Initial AI analysis
2. **Summarization** - Generate legal summary
3. **Classification** - Privilege and evidence detection
4. **Entity Extraction** - Extract legal entities
5. **Aggregation** - Combine results

#### **Optimized Pipeline (ediscovery_optimized.yaml)**
Parallel processing for faster throughput:
1. **Single API Call** - Batch process document
2. **Parallel Extraction** - Simultaneous analysis streams
3. **Result Aggregation** - Combine and structure results

### **Custom Workflows**

Create your own eDiscovery workflows:

```yaml
# workflows/custom_ediscovery.yaml
name: "Custom Legal Analysis"
description: "Specialized legal document processing"

nodes:
  - id: legal_review
    operator: LegalReviewOperator
    params:
      jurisdiction: "federal"
      practice_area: "patent"
  
  - id: compliance_check
    operator: ComplianceOperator
    params:
      regulations: ["FRCP", "FOIA"]

edges:
  - legal_review -> compliance_check
```

---

## 🏢 Enterprise Features

### **Compliance & Audit**
- **Complete Audit Trail**: Every document access and modification logged
- **Role-Based Access**: Granular permissions for attorneys, paralegals, clients
- **Data Retention**: Configurable retention policies per case
- **Export Controls**: Structured data export for discovery production

### **Security & Privacy**
- **Encryption**: At-rest and in-transit data encryption
- **Privilege Protection**: Automatic privilege identification and flagging
- **Access Controls**: Multi-factor authentication and session management
- **Privacy Preservation**: PII detection and redaction capabilities

### **Integration Capabilities**
- **Document Management**: Integration with SharePoint, NetDocuments
- **Practice Management**: Connect with Clio, PracticePanther
- **Review Platforms**: Export to Relativity, Concordance
- **Billing Systems**: Time tracking and cost allocation

### **Scalability**
- **Distributed Processing**: Horizontal scaling with multiple agents
- **Load Balancing**: Automatic workload distribution
- **Caching**: Intelligent result caching for performance
- **Monitoring**: Real-time performance and health monitoring

---

## 🧪 Development & Testing

### **Run Tests**
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# Elixir tests
mix test

# Integration tests
mix test --include integration
```

### **Code Quality**
```bash
# Python linting
cd backend
ruff check .
mypy .

# Frontend linting
cd frontend
npm run lint
npm run type-check

# Elixir formatting
mix format
mix credo
```

### **Development Workflow**
1. **Create Feature Branch**: `git checkout -b feature/new-analysis`
2. **Write Tests**: Test-driven development approach
3. **Implement Feature**: Code with type safety and documentation
4. **Run Quality Checks**: Linting, formatting, type checking
5. **Integration Test**: Test with full system running
6. **Submit PR**: Comprehensive code review process

---

## 🚀 Deployment

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or individually
docker build -t ediscovery-backend ./backend
docker build -t ediscovery-frontend ./frontend
```

### **Production Configuration**
```bash
# Environment variables for production
export NODE_ENV=production
export DATABASE_URL=mongodb://prod-mongo:27017/ediscovery
export OPENAI_API_KEY=prod-openai-key
export NATS_URL=nats://prod-nats:4222
export JWT_SECRET=your-jwt-secret
```

### **Monitoring & Observability**
- **Metrics**: Prometheus endpoints at `/metrics`
- **Logging**: Structured JSON logging with correlation IDs
- **Health Checks**: Kubernetes-ready health endpoints
- **Tracing**: OpenTelemetry integration for distributed tracing

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Ensure all checks pass: `make test lint`
5. Submit pull request

### **Code Standards**
- **TypeScript**: Strict type checking, comprehensive interfaces
- **Python**: Type hints, docstrings, PEP 8 compliance
- **Elixir**: Typespecs, documentation, Credo compliance
- **Documentation**: Comprehensive README and inline docs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Hypergraph Agents Framework**: Distributed AI workflow engine
- **OpenAI**: GPT models for intelligent document analysis
- **Legal Tech Community**: Inspiration for eDiscovery innovation
- **Open Source Contributors**: Making legal technology accessible

---

## 📞 Support & Contact

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/jmanhype/eDiscovery-Hypergraph/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jmanhype/eDiscovery-Hypergraph/discussions)
- **Email**: [support@ediscovery-hypergraph.com](mailto:support@ediscovery-hypergraph.com)

---

**Built with ❤️ for the Legal Technology Community**

*Empowering legal professionals with intelligent, scalable document analysis and eDiscovery capabilities.*