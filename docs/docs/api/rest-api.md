---
id: rest-api
title: REST API
sidebar_label: REST API
---

# REST API

The eDiscovery Hypergraph platform provides a comprehensive REST API for programmatic access to all platform features. This guide covers authentication, endpoints, and best practices.

## Base URL

```
https://api.ediscovery-hypergraph.com/v1
```

For local development:
```
http://localhost:4000/api/v1
```

## Authentication

### API Key Authentication

Include your API key in the `Authorization` header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.ediscovery-hypergraph.com/v1/cases
```

### JWT Authentication

For user-specific operations:

```bash
# Login to get JWT token
curl -X POST https://api.ediscovery-hypergraph.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'

# Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.ediscovery-hypergraph.com/v1/documents
```

## Core Endpoints

### Cases

#### List Cases

```http
GET /api/v1/cases
```

Query parameters:
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `status` (string): Filter by status (active, archived, on_hold)
- `client_id` (string): Filter by client
- `sort` (string): Sort field (created_at, updated_at, name)
- `order` (string): Sort order (asc, desc)

Response:
```json
{
  "data": [
    {
      "id": "case_123",
      "name": "Smith v. Jones",
      "description": "Contract dispute case",
      "client_id": "client_456",
      "status": "active",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-20T14:30:00Z",
      "metadata": {
        "case_number": "2024-CV-1234",
        "jurisdiction": "California",
        "judge": "Hon. Jane Doe"
      },
      "statistics": {
        "total_documents": 15420,
        "reviewed_documents": 8234,
        "privileged_documents": 523
      }
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_items": 94
  }
}
```

#### Create Case

```http
POST /api/v1/cases
```

Request body:
```json
{
  "name": "New Case Name",
  "description": "Case description",
  "client_id": "client_456",
  "metadata": {
    "case_number": "2024-CV-5678",
    "jurisdiction": "New York",
    "matter_type": "litigation"
  }
}
```

Response:
```json
{
  "data": {
    "id": "case_789",
    "name": "New Case Name",
    "status": "active",
    "created_at": "2024-01-21T09:00:00Z"
  }
}
```

#### Update Case

```http
PATCH /api/v1/cases/{case_id}
```

Request body:
```json
{
  "name": "Updated Case Name",
  "status": "on_hold",
  "metadata": {
    "settlement_date": "2024-02-15"
  }
}
```

### Documents

#### Upload Documents

```http
POST /api/v1/cases/{case_id}/documents/upload
```

Multipart form data:
- `files[]`: Array of files to upload
- `auto_process` (boolean): Start processing immediately
- `tags[]`: Array of tags to apply
- `metadata` (JSON): Additional metadata

Example using curl:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files[]=@document1.pdf" \
  -F "files[]=@document2.docx" \
  -F "auto_process=true" \
  -F "tags[]=contract" \
  -F "tags[]=confidential" \
  -F 'metadata={"source":"email","custodian":"john.doe@example.com"}' \
  https://api.ediscovery-hypergraph.com/v1/cases/case_123/documents/upload
```

Response:
```json
{
  "data": {
    "upload_id": "upload_abc123",
    "documents": [
      {
        "id": "doc_001",
        "filename": "document1.pdf",
        "size": 2048576,
        "status": "processing"
      },
      {
        "id": "doc_002",
        "filename": "document2.docx",
        "size": 512000,
        "status": "processing"
      }
    ],
    "processing_job_id": "job_xyz789"
  }
}
```

#### Search Documents

```http
POST /api/v1/documents/search
```

Request body:
```json
{
  "query": "contract breach damages",
  "filters": {
    "case_ids": ["case_123", "case_456"],
    "date_range": {
      "start": "2023-01-01",
      "end": "2023-12-31"
    },
    "document_types": ["email", "contract"],
    "privilege_status": ["not_privileged", "partially_privileged"],
    "has_entities": {
      "types": ["person", "organization"],
      "names": ["John Smith", "Acme Corp"]
    }
  },
  "search_type": "semantic",
  "include_snippets": true,
  "highlight": true,
  "page": 1,
  "per_page": 20,
  "sort": {
    "field": "relevance",
    "order": "desc"
  }
}
```

Response:
```json
{
  "data": {
    "results": [
      {
        "document_id": "doc_789",
        "case_id": "case_123",
        "title": "Contract Agreement - Acme Corp",
        "relevance_score": 0.95,
        "snippets": [
          "...the <mark>breach</mark> of <mark>contract</mark> resulted in significant <mark>damages</mark>..."
        ],
        "entities": [
          {
            "text": "Acme Corp",
            "type": "organization",
            "count": 15
          }
        ],
        "metadata": {
          "date": "2023-06-15",
          "author": "legal@acmecorp.com",
          "document_type": "contract"
        }
      }
    ],
    "facets": {
      "document_types": {
        "email": 234,
        "contract": 45,
        "memo": 78
      },
      "privilege_status": {
        "not_privileged": 298,
        "privileged": 45,
        "partially_privileged": 14
      }
    },
    "total_results": 357,
    "search_time_ms": 145
  }
}
```

#### Get Document Details

```http
GET /api/v1/documents/{document_id}
```

Query parameters:
- `include` (string): Comma-separated list of related data to include
  - `processing_results`: AI analysis results
  - `hypergraph_relations`: Related documents and entities
  - `audit_trail`: Access history
  - `versions`: Document version history

Response:
```json
{
  "data": {
    "id": "doc_789",
    "case_id": "case_123",
    "filename": "contract_final.pdf",
    "content_type": "application/pdf",
    "size": 2048576,
    "hash": "sha256:abcdef123456...",
    "status": "processed",
    "created_at": "2024-01-15T10:00:00Z",
    "processing_results": {
      "entities": [
        {
          "text": "John Smith",
          "type": "person",
          "role": "signatory",
          "confidence": 0.98
        }
      ],
      "privilege_analysis": {
        "is_privileged": false,
        "confidence": 0.95,
        "reasons": []
      },
      "summary": "Commercial contract between Acme Corp and Beta Inc...",
      "key_dates": [
        {
          "date": "2023-06-15",
          "description": "Contract execution date"
        }
      ],
      "monetary_amounts": [
        {
          "amount": 500000,
          "currency": "USD",
          "context": "Total contract value"
        }
      ]
    }
  }
}
```

### Processing

#### Process Documents

```http
POST /api/v1/documents/process
```

Request body:
```json
{
  "document_ids": ["doc_001", "doc_002", "doc_003"],
  "operations": [
    "text_extraction",
    "entity_extraction",
    "privilege_detection",
    "summarization",
    "translation"
  ],
  "options": {
    "language": "auto",
    "target_language": "en",
    "quality_mode": "high",
    "batch_size": 10
  },
  "workflow_id": "workflow_legal_review"
}
```

Response:
```json
{
  "data": {
    "job_id": "job_abc123",
    "status": "queued",
    "estimated_completion": "2024-01-21T11:30:00Z",
    "documents_queued": 3,
    "webhook_url": "https://api.ediscovery-hypergraph.com/v1/jobs/job_abc123/status"
  }
}
```

#### Get Processing Status

```http
GET /api/v1/jobs/{job_id}/status
```

Response:
```json
{
  "data": {
    "job_id": "job_abc123",
    "status": "in_progress",
    "progress": {
      "total_documents": 3,
      "completed": 2,
      "failed": 0,
      "percentage": 66.67
    },
    "current_operation": "entity_extraction",
    "started_at": "2024-01-21T10:00:00Z",
    "estimated_completion": "2024-01-21T10:15:00Z",
    "results": {
      "doc_001": {
        "status": "completed",
        "operations_completed": ["text_extraction", "entity_extraction"]
      },
      "doc_002": {
        "status": "completed",
        "operations_completed": ["text_extraction", "entity_extraction"]
      },
      "doc_003": {
        "status": "processing",
        "operations_completed": ["text_extraction"],
        "current_operation": "entity_extraction"
      }
    }
  }
}
```

### Workflows

#### List Workflows

```http
GET /api/v1/workflows
```

Query parameters:
- `type` (string): Filter by workflow type (system, custom, shared)
- `tags[]` (array): Filter by tags

Response:
```json
{
  "data": [
    {
      "id": "workflow_001",
      "name": "Standard Legal Review",
      "description": "Complete legal document review workflow",
      "type": "system",
      "version": "2.0",
      "tags": ["legal", "review", "production"],
      "nodes": [
        {
          "id": "extract",
          "operator": "TextExtractionOperator",
          "config": {}
        }
      ],
      "usage_count": 1523,
      "average_duration": "PT15M"
    }
  ]
}
```

#### Execute Workflow

```http
POST /api/v1/workflows/{workflow_id}/execute
```

Request body:
```json
{
  "input": {
    "document_ids": ["doc_001", "doc_002"],
    "case_id": "case_123"
  },
  "parameters": {
    "confidence_threshold": 0.9,
    "include_human_review": true
  },
  "execution_options": {
    "priority": "high",
    "timeout_minutes": 60,
    "webhook_url": "https://your-app.com/webhook"
  }
}
```

Response:
```json
{
  "data": {
    "execution_id": "exec_xyz789",
    "workflow_id": "workflow_001",
    "status": "running",
    "started_at": "2024-01-21T10:00:00Z",
    "tracking_url": "https://app.ediscovery-hypergraph.com/executions/exec_xyz789"
  }
}
```

### Analytics

#### Get Case Analytics

```http
GET /api/v1/cases/{case_id}/analytics
```

Query parameters:
- `metrics[]` (array): Specific metrics to include
- `date_range` (string): Time period (last_7_days, last_30_days, custom)
- `group_by` (string): Grouping dimension (day, week, document_type)

Response:
```json
{
  "data": {
    "case_id": "case_123",
    "period": "last_30_days",
    "metrics": {
      "document_statistics": {
        "total": 15420,
        "processed": 14890,
        "pending": 530,
        "failed": 0
      },
      "privilege_analysis": {
        "privileged": 1523,
        "not_privileged": 13367,
        "review_required": 530,
        "privilege_types": {
          "attorney_client": 890,
          "work_product": 633
        }
      },
      "entity_statistics": {
        "unique_people": 234,
        "unique_organizations": 89,
        "unique_locations": 45,
        "most_mentioned": [
          {
            "entity": "John Smith",
            "type": "person",
            "mentions": 523
          }
        ]
      },
      "processing_performance": {
        "average_time_per_document": 2.3,
        "total_processing_time": 592.5,
        "ai_api_calls": 45230,
        "ai_tokens_used": 12500000
      }
    },
    "time_series": {
      "documents_processed": [
        {
          "date": "2024-01-01",
          "count": 523
        }
      ]
    }
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "case_id",
        "message": "Case not found"
      }
    ],
    "request_id": "req_abc123",
    "documentation_url": "https://docs.ediscovery-hypergraph.com/errors/VALIDATION_ERROR"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid authentication |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Temporary service disruption |

## Rate Limiting

Rate limits are enforced per API key:

- **Standard tier**: 100 requests per minute
- **Professional tier**: 1,000 requests per minute
- **Enterprise tier**: Custom limits

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642789200
```

## Webhooks

### Webhook Configuration

```http
POST /api/v1/webhooks
```

Request body:
```json
{
  "url": "https://your-app.com/webhook",
  "events": [
    "document.processed",
    "workflow.completed",
    "case.updated"
  ],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload

```json
{
  "id": "evt_123",
  "type": "document.processed",
  "created_at": "2024-01-21T10:00:00Z",
  "data": {
    "document_id": "doc_789",
    "case_id": "case_123",
    "processing_results": {
      "status": "completed",
      "operations": ["text_extraction", "entity_extraction"]
    }
  }
}
```

### Webhook Security

Verify webhook signatures:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)
```

## SDK Examples

### Python SDK

```python
from ediscovery_hypergraph import Client

client = Client(api_key="YOUR_API_KEY")

# List cases
cases = client.cases.list(status="active")

# Upload documents
case = client.cases.get("case_123")
upload_result = case.documents.upload(
    files=["document1.pdf", "document2.docx"],
    auto_process=True,
    tags=["contract", "confidential"]
)

# Search documents
results = client.documents.search(
    query="breach of contract",
    filters={
        "case_ids": ["case_123"],
        "date_range": {
            "start": "2023-01-01",
            "end": "2023-12-31"
        }
    },
    search_type="semantic"
)

# Execute workflow
workflow = client.workflows.get("workflow_legal_review")
execution = workflow.execute(
    input={
        "document_ids": ["doc_001", "doc_002"],
        "case_id": "case_123"
    },
    parameters={
        "confidence_threshold": 0.9
    }
)

# Monitor execution
while execution.status == "running":
    execution.refresh()
    print(f"Progress: {execution.progress}%")
    time.sleep(5)
```

### JavaScript/TypeScript SDK

```typescript
import { EdiscoveryClient } from '@ediscovery-hypergraph/sdk';

const client = new EdiscoveryClient({
  apiKey: 'YOUR_API_KEY'
});

// Async/await example
async function processDocuments() {
  // List cases
  const cases = await client.cases.list({ status: 'active' });
  
  // Upload documents
  const uploadResult = await client.documents.upload({
    caseId: 'case_123',
    files: [file1, file2],
    autoProcess: true,
    metadata: {
      source: 'email',
      custodian: 'john.doe@example.com'
    }
  });
  
  // Search with real-time updates
  const searchStream = client.documents.searchStream({
    query: 'contract breach',
    filters: {
      caseIds: ['case_123']
    }
  });
  
  searchStream.on('result', (result) => {
    console.log('Found document:', result);
  });
  
  searchStream.on('complete', (summary) => {
    console.log('Search complete:', summary);
  });
}
```

## Best Practices

### 1. Pagination

Always use pagination for list endpoints:

```python
def get_all_documents(case_id):
    documents = []
    page = 1
    
    while True:
        response = client.get(f"/cases/{case_id}/documents", params={
            "page": page,
            "per_page": 100
        })
        
        documents.extend(response["data"])
        
        if page >= response["pagination"]["total_pages"]:
            break
            
        page += 1
    
    return documents
```

### 2. Error Handling

Implement robust error handling:

```python
def api_request_with_retry(method, url, **kwargs):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                retry_after = int(e.response.headers.get('Retry-After', retry_delay))
                time.sleep(retry_after)
                retry_delay *= 2
            elif e.response.status_code >= 500:  # Server error
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
            else:
                raise  # Client error, don't retry
```

### 3. Batch Operations

Use batch endpoints when available:

```python
# Instead of individual requests
for doc_id in document_ids:
    client.post(f"/documents/{doc_id}/process")

# Use batch endpoint
client.post("/documents/process", json={
    "document_ids": document_ids,
    "operations": ["entity_extraction", "summarization"]
})
```

## Next Steps

- Explore [GraphQL API](/api/graphql-api) for complex queries
- Learn about [WebSocket API](/api/websocket-api) for real-time updates
- Review [Examples](/examples) for common use cases
- Check [Support](/support) for additional help