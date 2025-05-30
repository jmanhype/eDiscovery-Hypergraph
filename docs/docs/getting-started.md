---
id: getting-started
title: Getting Started
sidebar_label: Getting Started
---

# Getting Started with eDiscovery Hypergraph

This guide will help you set up and start using the eDiscovery Hypergraph platform in under 10 minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** and **Docker Compose** (recommended) OR
- **Elixir** 1.14+ with Erlang/OTP 25+
- **Python** 3.8+
- **Node.js** 18+ and Yarn
- **MongoDB** 4.4+
- **NATS Server** 2.9+
- **OpenAI API Key** for AI features

## Quick Start with Docker

The fastest way to get started is using Docker:

```bash
# Clone the repository
git clone https://github.com/your-org/ediscovery-hypergraph.git
cd ediscovery-hypergraph

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Start all services
docker-compose up

# Access the application
open http://localhost:3000
```

## Manual Installation

### 1. Install Dependencies

```bash
# macOS with Homebrew
brew install elixir mongodb-community nats-server

# Start services
brew services start mongodb-community
brew services start nats-server
```

### 2. Set Up the Backend

```bash
# Install Elixir dependencies
mix deps.get
mix deps.compile

# Set up Python environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 3. Set Up the Frontend

```bash
cd frontend
yarn install
cd ..
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Database Configuration
MONGODB_URL=mongodb://localhost:27017/ediscovery

# Service Ports
PHOENIX_PORT=4000
PYTHON_API_PORT=8001
FRONTEND_PORT=3000

# NATS Configuration
NATS_URL=nats://localhost:4222
```

### 5. Start the Services

Open three terminal windows:

**Terminal 1 - Elixir/Phoenix Backend:**
```bash
iex -S mix phx.server
```

**Terminal 2 - Python AI Service:**
```bash
cd backend
OPENAI_API_KEY=$OPENAI_API_KEY python server.py
```

**Terminal 3 - React Frontend:**
```bash
cd frontend
yarn start
```

## Your First Document Processing

### 1. Access the Platform

Navigate to [http://localhost:3000](http://localhost:3000) and log in with the default credentials:
- Username: `admin@example.com`
- Password: `admin123`

### 2. Create a New Case

1. Click **"New Case"** in the dashboard
2. Enter case details:
   - Name: "Sample Litigation Case"
   - Description: "Testing document processing"
   - Client: "Acme Corp"
3. Click **"Create Case"**

### 3. Upload Documents

1. Navigate to your case
2. Click **"Upload Documents"**
3. Select sample documents or drag and drop files
4. Click **"Start Processing"**

### 4. Monitor Processing

The platform will automatically:
- Extract text from documents
- Identify entities (people, organizations, locations)
- Classify for legal privilege
- Generate summaries
- Build relationship graphs

### 5. Review Results

Once processing completes:
- View AI-generated summaries
- Check privilege classifications
- Explore entity relationships
- Search across all processed content

## Testing with Sample Data

We provide sample legal documents for testing:

```bash
# Download sample documents
curl -O https://raw.githubusercontent.com/your-org/ediscovery-hypergraph/main/samples/legal-docs.zip
unzip legal-docs.zip

# Process via API
curl -X POST http://localhost:8001/api/ediscovery/process \
  -H "Content-Type: application/json" \
  -d '{
    "email": "From: john@acme.com\nTo: legal@acme.com\nSubject: Contract Review\n\nPlease review the attached contract with our attorney."
  }'
```

## Using the Workflow Engine

Create a custom workflow:

```yaml
# workflows/my-workflow.yaml
name: "Custom Document Analysis"
nodes:
  - id: extract_entities
    op: EdiscoveryEntityExtractionOperator
  - id: classify_privilege
    op: EdiscoveryClassificationOperator
    depends_on: [extract_entities]
  - id: summarize
    op: EdiscoverySummarizationOperator
    depends_on: [classify_privilege]
```

Run the workflow:

```bash
mix workflow.run workflows/my-workflow.yaml \
  --json '{"email":"Your document content here"}'
```

## Next Steps

Now that you have the platform running:

1. **Explore Features**: Learn about [AI Analysis](/features/ai-analysis), [Search](/features/search), and [Workflows](/features/workflows)
2. **Understand Architecture**: Deep dive into the [system architecture](/architecture/overview)
3. **API Integration**: Connect your applications using our [REST](/api/rest) and [GraphQL](/api/graphql) APIs
4. **Deploy to Production**: Follow our [production deployment guide](/deployment/production)

## Troubleshooting

### Common Issues

**MongoDB Connection Error:**
```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Start MongoDB if needed
brew services start mongodb-community
```

**NATS Connection Error:**
```bash
# Start NATS server
nats-server
# Or as a service: brew services start nats-server
```

**OpenAI API Error:**
```bash
# Verify your API key is set
echo $OPENAI_API_KEY

# Test the API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Getting Help

- Check our [FAQ](/support#faq)
- Join our [Slack community](https://slack.ediscovery-hypergraph.com)
- Open an issue on [GitHub](https://github.com/your-org/ediscovery-hypergraph/issues)

## What's Next?

Congratulations! You've successfully set up the eDiscovery Hypergraph platform. Here are some recommended next steps:

- [Create your first workflow](/features/workflows)
- [Integrate with your existing systems](/api/rest)
- [Set up user roles and permissions](/features/compliance#access-control)
- [Configure advanced AI settings](/features/ai-analysis#configuration)