---
id: graphql-api
title: GraphQL API
sidebar_label: GraphQL API
---

# GraphQL API

The eDiscovery Hypergraph platform provides a powerful GraphQL API that enables complex queries, real-time subscriptions, and efficient data fetching with minimal network overhead.

## Endpoint

```
https://api.ediscovery-hypergraph.com/graphql
```

For local development:
```
http://localhost:4000/graphql
```

## GraphQL Playground

Access the interactive GraphQL playground at:
```
https://api.ediscovery-hypergraph.com/graphiql
```

## Authentication

Include your authentication token in the `Authorization` header:

```json
{
  "Authorization": "Bearer YOUR_TOKEN"
}
```

## Schema Overview

### Core Types

```graphql
type Case {
  id: ID!
  name: String!
  description: String
  clientId: ID!
  client: Client
  status: CaseStatus!
  createdAt: DateTime!
  updatedAt: DateTime!
  metadata: JSON
  documents(
    filter: DocumentFilter
    pagination: PaginationInput
    sort: DocumentSort
  ): DocumentConnection!
  statistics: CaseStatistics!
  workflows: [Workflow!]!
  team: [TeamMember!]!
}

type Document {
  id: ID!
  caseId: ID!
  case: Case!
  filename: String!
  contentType: String!
  size: Int!
  hash: String!
  status: DocumentStatus!
  createdAt: DateTime!
  processingResults: ProcessingResults
  hypergraphNode: HypergraphNode
  privileges: [PrivilegeAnalysis!]
  entities: [Entity!]!
  relatedDocuments(limit: Int): [Document!]!
  versions: [DocumentVersion!]!
  audit: AuditTrail!
}

type Entity {
  id: ID!
  text: String!
  type: EntityType!
  normalizedText: String
  confidence: Float!
  metadata: JSON
  documents(filter: DocumentFilter): [Document!]!
  relationships: [EntityRelationship!]!
  hypergraphNode: HypergraphNode
}

type HypergraphNode {
  id: ID!
  type: NodeType!
  properties: JSON!
  hyperedges: [Hyperedge!]!
  connectedNodes(
    type: NodeType
    limit: Int
    maxDistance: Int
  ): [HypergraphNode!]!
}

type Hyperedge {
  id: ID!
  type: HyperedgeType!
  nodes: [HypergraphNode!]!
  properties: JSON!
  weight: Float!
  createdAt: DateTime!
}
```

## Queries

### Get Case with Documents

```graphql
query GetCaseDetails($caseId: ID!) {
  case(id: $caseId) {
    id
    name
    description
    status
    client {
      id
      name
      contactEmail
    }
    statistics {
      totalDocuments
      processedDocuments
      privilegedDocuments
      totalEntities
      uniquePeople
      uniqueOrganizations
    }
    documents(
      filter: {
        status: PROCESSED
        hasPrivilege: true
      }
      pagination: {
        limit: 20
        offset: 0
      }
      sort: {
        field: CREATED_AT
        direction: DESC
      }
    ) {
      edges {
        node {
          id
          filename
          processingResults {
            privilege {
              isPrivileged
              type
              confidence
            }
            summary
          }
          entities(type: PERSON) {
            text
            confidence
          }
        }
      }
      pageInfo {
        hasNextPage
        totalCount
      }
    }
  }
}
```

### Complex Document Search

```graphql
query SearchDocuments($searchInput: DocumentSearchInput!) {
  searchDocuments(input: $searchInput) {
    results {
      document {
        id
        filename
        case {
          name
        }
        processingResults {
          summary
        }
      }
      score
      highlights {
        field
        snippets
      }
      matchedEntities {
        entity {
          text
          type
        }
        frequency
      }
    }
    facets {
      documentTypes {
        value
        count
      }
      dateRanges {
        range
        count
      }
      privilegeStatus {
        status
        count
      }
    }
    totalCount
    searchTime
  }
}
```

Variables:
```json
{
  "searchInput": {
    "query": "breach of contract damages",
    "filters": {
      "caseIds": ["case_123", "case_456"],
      "dateRange": {
        "start": "2023-01-01",
        "end": "2023-12-31"
      },
      "entityNames": ["John Smith", "Acme Corp"],
      "privilegeStatus": ["NOT_PRIVILEGED", "PARTIALLY_PRIVILEGED"]
    },
    "searchType": "SEMANTIC",
    "includeRelated": true,
    "pagination": {
      "limit": 20,
      "offset": 0
    }
  }
}
```

### Hypergraph Traversal

```graphql
query ExploreHypergraph($nodeId: ID!, $depth: Int!) {
  hypergraphNode(id: $nodeId) {
    id
    type
    properties
    
    # Direct hyperedges
    hyperedges {
      id
      type
      weight
      nodes {
        id
        type
        ... on DocumentNode {
          document {
            filename
            summary
          }
        }
        ... on EntityNode {
          entity {
            text
            type
          }
        }
      }
    }
    
    # Traverse the hypergraph
    connectedNodes(maxDistance: $depth) {
      id
      type
      distance
      pathStrength
      ... on DocumentNode {
        document {
          id
          filename
        }
      }
    }
    
    # Find privilege groups
    privilegeGroups: hyperedges(type: PRIVILEGE) {
      id
      properties
      nodes {
        ... on DocumentNode {
          document {
            id
            filename
          }
        }
      }
    }
  }
}
```

### Entity Relationship Analysis

```graphql
query AnalyzeEntityRelationships($entityId: ID!) {
  entity(id: $entityId) {
    id
    text
    type
    
    # Direct relationships
    relationships {
      id
      type
      relatedEntity {
        id
        text
        type
      }
      strength
      evidence {
        documentId
        context
      }
    }
    
    # Co-occurrence analysis
    coOccurrences(minFrequency: 5) {
      entity {
        id
        text
        type
      }
      frequency
      documents {
        id
        filename
      }
    }
    
    # Communication network
    communications {
      withEntity {
        id
        text
      }
      messageCount
      dateRange {
        start
        end
      }
      topics
    }
    
    # Timeline of mentions
    timeline {
      date
      documentCount
      keyEvents {
        document {
          id
          filename
        }
        context
      }
    }
  }
}
```

## Mutations

### Create Case

```graphql
mutation CreateCase($input: CreateCaseInput!) {
  createCase(input: $input) {
    case {
      id
      name
      status
      createdAt
    }
    errors {
      field
      message
    }
  }
}
```

Variables:
```json
{
  "input": {
    "name": "Smith v. Jones",
    "description": "Contract dispute regarding software development",
    "clientId": "client_123",
    "metadata": {
      "caseNumber": "2024-CV-1234",
      "jurisdiction": "California",
      "estimatedDocuments": 50000
    },
    "teamMemberIds": ["user_456", "user_789"]
  }
}
```

### Upload and Process Documents

```graphql
mutation UploadDocuments($input: UploadDocumentsInput!) {
  uploadDocuments(input: $input) {
    upload {
      id
      documents {
        id
        filename
        status
        processingJob {
          id
          status
          estimatedCompletion
        }
      }
    }
    errors {
      field
      message
    }
  }
}
```

### Execute Workflow

```graphql
mutation ExecuteWorkflow($input: ExecuteWorkflowInput!) {
  executeWorkflow(input: $input) {
    execution {
      id
      workflowId
      status
      startedAt
      nodes {
        id
        status
        startedAt
        completedAt
        result
        error
      }
    }
    errors {
      field
      message
    }
  }
}
```

Variables:
```json
{
  "input": {
    "workflowId": "workflow_legal_review",
    "parameters": {
      "documentIds": ["doc_001", "doc_002"],
      "caseId": "case_123",
      "confidenceThreshold": 0.9,
      "includeTranslation": true
    },
    "executionOptions": {
      "priority": "HIGH",
      "notifyOnCompletion": true
    }
  }
}
```

### Update Document Privilege

```graphql
mutation UpdateDocumentPrivilege($input: UpdatePrivilegeInput!) {
  updateDocumentPrivilege(input: $input) {
    document {
      id
      privileges {
        isPrivileged
        type
        confidence
        reviewedBy {
          id
          name
        }
        reviewedAt
      }
    }
    auditEntry {
      id
      action
      timestamp
      user {
        id
        name
      }
    }
  }
}
```

## Subscriptions

### Real-time Document Processing

```graphql
subscription DocumentProcessing($caseId: ID!) {
  documentProcessingUpdates(caseId: $caseId) {
    documentId
    status
    progress
    currentOperation
    completedOperations
    errors {
      operation
      message
    }
    estimatedCompletion
  }
}
```

### Workflow Execution Updates

```graphql
subscription WorkflowExecution($executionId: ID!) {
  workflowExecutionUpdates(executionId: $executionId) {
    executionId
    status
    currentNode {
      id
      name
      status
      progress
    }
    completedNodes
    totalNodes
    errors {
      nodeId
      error
      retryCount
    }
    metrics {
      duration
      documentsProcessed
      entitiesExtracted
    }
  }
}
```

### Case Activity Feed

```graphql
subscription CaseActivity($caseId: ID!) {
  caseActivityFeed(caseId: $caseId) {
    id
    type
    timestamp
    user {
      id
      name
      avatar
    }
    data {
      ... on DocumentUploadActivity {
        documentCount
        totalSize
      }
      ... on PrivilegeReviewActivity {
        documentId
        decision
        reason
      }
      ... on WorkflowCompletedActivity {
        workflowName
        duration
        documentsProcessed
      }
    }
  }
}
```

## Error Handling

GraphQL errors follow a consistent format:

```json
{
  "data": null,
  "errors": [
    {
      "message": "Document not found",
      "extensions": {
        "code": "RESOURCE_NOT_FOUND",
        "documentId": "doc_123",
        "timestamp": "2024-01-21T10:00:00Z"
      },
      "path": ["document"],
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ]
    }
  ]
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `UNAUTHENTICATED` | Missing or invalid authentication |
| `FORBIDDEN` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `VALIDATION_ERROR` | Invalid input parameters |
| `INTERNAL_ERROR` | Server error |
| `RATE_LIMITED` | Too many requests |
| `COMPLEXITY_ERROR` | Query too complex |

## Query Complexity

To prevent abuse, queries are limited by complexity:

```graphql
# Complexity calculation example
query ComplexQuery {
  cases(limit: 100) {           # Complexity: 100
    documents(limit: 50) {      # Complexity: 100 * 50 = 5000
      entities(limit: 20) {     # Complexity: 5000 * 20 = 100,000
        text
      }
    }
  }
}
# Total complexity: 100,000 (may exceed limit)
```

### Complexity Limits

- **Anonymous**: 1,000 points
- **Authenticated**: 10,000 points
- **Enterprise**: Custom limits

## Best Practices

### 1. Use Fragments

```graphql
fragment DocumentDetails on Document {
  id
  filename
  status
  processingResults {
    summary
    privilege {
      isPrivileged
      type
      confidence
    }
  }
}

query GetCaseDocuments($caseId: ID!) {
  case(id: $caseId) {
    documents {
      edges {
        node {
          ...DocumentDetails
        }
      }
    }
  }
}
```

### 2. Pagination

Always paginate large result sets:

```graphql
query PaginatedDocuments($caseId: ID!, $cursor: String) {
  case(id: $caseId) {
    documents(first: 20, after: $cursor) {
      edges {
        node {
          id
          filename
        }
        cursor
      }
      pageInfo {
        hasNextPage
        endCursor
        totalCount
      }
    }
  }
}
```

### 3. Field Selection

Only request fields you need:

```graphql
# Bad - requests everything
query GetDocument($id: ID!) {
  document(id: $id) {
    ... # All fields
  }
}

# Good - specific fields
query GetDocumentSummary($id: ID!) {
  document(id: $id) {
    id
    filename
    processingResults {
      summary
    }
  }
}
```

### 4. Batch Queries

Combine related queries:

```graphql
query BatchedQueries($caseId: ID!, $userId: ID!) {
  case(id: $caseId) {
    name
    statistics {
      totalDocuments
    }
  }
  
  user(id: $userId) {
    name
    permissions
  }
  
  recentActivity(caseId: $caseId, limit: 10) {
    type
    timestamp
  }
}
```

## Client Libraries

### JavaScript/TypeScript

```typescript
import { GraphQLClient } from 'graphql-request';

const client = new GraphQLClient('https://api.ediscovery-hypergraph.com/graphql', {
  headers: {
    authorization: `Bearer ${token}`,
  },
});

// Simple query
const GET_CASE = gql`
  query GetCase($id: ID!) {
    case(id: $id) {
      id
      name
      statistics {
        totalDocuments
      }
    }
  }
`;

const data = await client.request(GET_CASE, { id: 'case_123' });

// With Apollo Client
import { ApolloClient, InMemoryCache } from '@apollo/client';

const apolloClient = new ApolloClient({
  uri: 'https://api.ediscovery-hypergraph.com/graphql',
  cache: new InMemoryCache(),
  headers: {
    authorization: `Bearer ${token}`,
  },
});

// Subscription
const DOCUMENT_UPDATES = gql`
  subscription DocumentUpdates($caseId: ID!) {
    documentProcessingUpdates(caseId: $caseId) {
      documentId
      status
      progress
    }
  }
`;

const subscription = apolloClient.subscribe({
  query: DOCUMENT_UPDATES,
  variables: { caseId: 'case_123' },
}).subscribe({
  next: (data) => console.log('Update:', data),
  error: (err) => console.error('Error:', err),
});
```

### Python

```python
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Configure transport
transport = AIOHTTPTransport(
    url="https://api.ediscovery-hypergraph.com/graphql",
    headers={"Authorization": f"Bearer {token}"}
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Execute query
query = gql("""
    query GetCase($id: ID!) {
        case(id: $id) {
            id
            name
            documents(first: 10) {
                edges {
                    node {
                        id
                        filename
                    }
                }
            }
        }
    }
""")

result = client.execute(query, variable_values={"id": "case_123"})

# Async execution
import asyncio

async def get_documents():
    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        query = gql("""
            query SearchDocuments($query: String!) {
                searchDocuments(input: { query: $query }) {
                    results {
                        document {
                            id
                            filename
                        }
                        score
                    }
                }
            }
        """)
        
        result = await session.execute(
            query,
            variable_values={"query": "contract breach"}
        )
        
        return result

# Subscriptions
from gql.transport.websockets import WebsocketsTransport

ws_transport = WebsocketsTransport(
    url="wss://api.ediscovery-hypergraph.com/graphql",
    headers={"Authorization": f"Bearer {token}"}
)

subscription = gql("""
    subscription CaseActivity($caseId: ID!) {
        caseActivityFeed(caseId: $caseId) {
            type
            timestamp
            user {
                name
            }
        }
    }
""")

async with Client(transport=ws_transport) as session:
    async for result in session.subscribe(
        subscription,
        variable_values={"caseId": "case_123"}
    ):
        print(f"Activity: {result}")
```

## Performance Tips

### 1. Use DataLoader Pattern

Prevent N+1 queries:

```typescript
// DataLoader implementation
const documentLoader = new DataLoader(async (ids) => {
  const documents = await fetchDocumentsByIds(ids);
  return ids.map(id => documents.find(doc => doc.id === id));
});

// In resolver
const resolvers = {
  Entity: {
    documents: (entity) => documentLoader.loadMany(entity.documentIds),
  },
};
```

### 2. Query Caching

```graphql
query CachedQuery @cacheControl(maxAge: 300) {
  cases {
    id
    name @cacheControl(maxAge: 3600)
    statistics @cacheControl(maxAge: 60)
  }
}
```

### 3. Defer Heavy Fields

```graphql
query GetDocument($id: ID!) {
  document(id: $id) {
    id
    filename
    
    # Defer expensive operations
    processingResults @defer {
      entities {
        text
        type
      }
      summary
    }
  }
}
```

## Next Steps

- Explore [WebSocket API](/api/websocket-api) for real-time features
- Review [REST API](/api/rest-api) for simpler operations
- Check [Examples](/examples) for common patterns
- Visit [Support](/support) for help