---
id: examples
title: Examples
sidebar_label: Examples
---

# Examples

This page provides practical examples and code snippets for common use cases in the eDiscovery Hypergraph platform.

## Quick Start Examples

### 1. Basic Document Processing

```python
# Python Example: Process a single document
import asyncio
from ediscovery_client import Client

async def process_document():
    # Initialize client
    client = Client(api_key="your-api-key")
    
    # Upload and process document
    with open("contract.pdf", "rb") as f:
        result = await client.documents.upload_and_process(
            file=f,
            case_id="case_123",
            operations=["extract", "analyze", "classify"],
            metadata={
                "source": "email_attachment",
                "custodian": "john.doe@example.com",
                "date_received": "2024-01-15"
            }
        )
    
    print(f"Document ID: {result.document_id}")
    print(f"Status: {result.status}")
    print(f"Extracted entities: {result.entities}")
    print(f"Privilege status: {result.privilege}")
    print(f"Summary: {result.summary}")

# Run the async function
asyncio.run(process_document())
```

### 2. Batch Document Upload

```javascript
// JavaScript Example: Batch upload with progress tracking
import { EdiscoveryClient } from '@ediscovery/sdk';

const client = new EdiscoveryClient({
  apiKey: process.env.EDISCOVERY_API_KEY
});

async function batchUpload(files) {
  const uploadSession = await client.documents.createBatchUpload({
    caseId: 'case_123',
    totalFiles: files.length
  });
  
  // Upload files with progress tracking
  const uploadPromises = files.map(async (file, index) => {
    const result = await uploadSession.uploadFile(file, {
      onProgress: (progress) => {
        console.log(`File ${index + 1}: ${progress.percent}% uploaded`);
      }
    });
    return result;
  });
  
  // Wait for all uploads
  const results = await Promise.all(uploadPromises);
  
  // Start processing
  const processingJob = await uploadSession.startProcessing({
    workflow: 'standard_legal_review',
    priority: 'high'
  });
  
  // Monitor processing
  processingJob.on('progress', (update) => {
    console.log(`Processing: ${update.completedDocuments}/${update.totalDocuments}`);
  });
  
  processingJob.on('complete', (summary) => {
    console.log('Processing complete:', summary);
  });
  
  return processingJob.wait();
}

// Usage
const files = [
  new File(['content'], 'document1.pdf'),
  new File(['content'], 'document2.docx')
];

batchUpload(files).then(results => {
  console.log('All documents processed:', results);
});
```

## Search Examples

### 3. Advanced Search with Facets

```python
# Complex search with multiple filters and facets
async def advanced_search():
    client = Client(api_key="your-api-key")
    
    # Semantic search with filters
    results = await client.search.documents(
        # Natural language query
        query="breach of contract regarding software licensing",
        
        # Search configuration
        search_type="semantic",
        
        # Filters
        filters={
            "case_ids": ["case_123", "case_456"],
            "date_range": {
                "start": "2023-01-01",
                "end": "2023-12-31"
            },
            "document_types": ["email", "contract", "memo"],
            "entities": {
                "organizations": ["Acme Corp", "TechCo Inc"],
                "people": ["John Smith", "Jane Doe"]
            },
            "privilege_status": ["not_privileged", "redacted"],
            "tags": {
                "include": ["important", "reviewed"],
                "exclude": ["draft"]
            }
        },
        
        # Facet configuration
        facets=["document_type", "author", "privilege_status", "date_histogram"],
        
        # Results configuration
        page=1,
        per_page=20,
        highlight=True,
        include_snippets=True,
        snippet_length=200
    )
    
    # Display results
    print(f"Found {results.total} documents in {results.search_time}ms")
    
    # Show facets
    for facet_name, facet_data in results.facets.items():
        print(f"\n{facet_name}:")
        for value, count in facet_data.items():
            print(f"  {value}: {count}")
    
    # Display results
    for doc in results.documents:
        print(f"\nDocument: {doc.filename}")
        print(f"Score: {doc.relevance_score}")
        print(f"Snippets: {doc.snippets}")
        
        # Show highlighted matches
        if doc.highlights:
            for field, highlights in doc.highlights.items():
                print(f"  {field}: {highlights}")

asyncio.run(advanced_search())
```

### 4. Entity Relationship Search

```graphql
# GraphQL Example: Find all documents related to specific entities
query EntityRelationshipSearch($entityName: String!) {
  entity(name: $entityName) {
    id
    type
    normalizedName
    
    # Direct document mentions
    documents(first: 100) {
      edges {
        node {
          id
          filename
          case {
            name
          }
          mentionContext {
            text
            position
            confidence
          }
        }
      }
    }
    
    # Related entities
    relatedEntities(minCooccurrence: 5) {
      entity {
        name
        type
      }
      cooccurrenceCount
      relationshipType
      sharedDocuments(first: 10) {
        id
        filename
      }
    }
    
    # Communication patterns
    communications {
      withEntity {
        name
        type
      }
      messageCount
      dateRange {
        start
        end
      }
      sentiment {
        positive
        negative
        neutral
      }
    }
    
    # Timeline of activity
    activityTimeline(
      groupBy: WEEK
      dateRange: { start: "2023-01-01", end: "2023-12-31" }
    ) {
      date
      documentCount
      keyEvents {
        type
        description
        documents {
          id
          filename
        }
      }
    }
  }
}
```

## Workflow Examples

### 5. Custom eDiscovery Workflow

```yaml
# custom_ediscovery_workflow.yaml
name: "Advanced Legal Review Workflow"
version: "1.0"
description: "Comprehensive document review with quality checks"

# Input parameters
parameters:
  confidence_threshold:
    type: float
    default: 0.85
    description: "Minimum confidence for automated decisions"
  
  require_human_review:
    type: boolean
    default: false
    description: "Force human review for all documents"
  
  languages:
    type: array
    default: ["en"]
    description: "Supported languages for processing"

# Workflow definition
nodes:
  # Initial validation
  - id: validate_input
    operator: ValidateInputOperator
    config:
      required_fields: ["document_id", "case_id"]
      max_file_size: 104857600  # 100MB
  
  # Language detection and routing
  - id: detect_language
    operator: LanguageDetectionOperator
    depends_on: [validate_input]
    config:
      supported_languages: ${parameters.languages}
  
  # Conditional translation
  - id: translate_if_needed
    operator: ConditionalOperator
    depends_on: [detect_language]
    config:
      condition: "output.detect_language.language != 'en'"
      true_operator:
        type: TranslationOperator
        config:
          target_language: "en"
          preserve_original: true
      false_operator:
        type: PassThroughOperator
  
  # Parallel AI analysis
  - id: ai_analysis
    operator: ParallelOperator
    depends_on: [translate_if_needed]
    config:
      operators:
        - type: EntityExtractionOperator
          config:
            model: "legal-ner-v2"
            include_confidence: true
        
        - type: PrivilegeClassificationOperator
          config:
            model: "privilege-bert-v3"
            include_factors: true
            threshold: ${parameters.confidence_threshold}
        
        - type: SummarizationOperator
          config:
            model: "gpt-4-turbo"
            max_length: 500
            style: "legal_brief"
        
        - type: SentimentAnalysisOperator
          config:
            granularity: "paragraph"
  
  # Quality assurance
  - id: quality_check
    operator: QualityAssuranceOperator
    depends_on: [ai_analysis]
    config:
      checks:
        - type: "entity_consistency"
          threshold: 0.9
        - type: "privilege_logic"
          validate_reasoning: true
        - type: "summary_coverage"
          min_coverage: 0.8
  
  # Human review decision
  - id: review_decision
    operator: BranchOperator
    depends_on: [quality_check]
    config:
      branches:
        - condition: "${parameters.require_human_review} == true"
          operator: HumanReviewOperator
        
        - condition: "output.quality_check.passed == false"
          operator: HumanReviewOperator
        
        - condition: "output.ai_analysis.privilege.confidence < ${parameters.confidence_threshold}"
          operator: HumanReviewOperator
        
        - default: true
          operator: AutoApproveOperator
  
  # Generate final report
  - id: generate_report
    operator: ReportGeneratorOperator
    depends_on: [review_decision]
    config:
      template: "legal_review_report"
      include_confidence_scores: true
      include_processing_metadata: true
      format: "pdf"

# Error handling
error_handling:
  default_strategy: "retry_with_backoff"
  max_retries: 3
  
  operator_strategies:
    TranslationOperator:
      strategy: "fallback"
      fallback_operator: "PassThroughOperator"
    
    HumanReviewOperator:
      strategy: "queue"
      timeout: 86400  # 24 hours
      escalation_email: "legal-team@example.com"

# Monitoring configuration
monitoring:
  metrics:
    - "processing_time_per_operator"
    - "confidence_scores"
    - "error_rate"
    - "human_review_rate"
  
  alerts:
    - metric: "error_rate"
      threshold: 0.05
      action: "email"
      recipients: ["ops@example.com"]
    
    - metric: "processing_time_per_operator"
      threshold: 300000  # 5 minutes
      action: "slack"
      channel: "#ediscovery-alerts"
```

### 6. Implementing Custom Operators

```elixir
# lib/operators/custom_classification_operator.ex
defmodule Operators.CustomClassificationOperator do
  @moduledoc """
  Custom operator for industry-specific document classification
  """
  
  use Operator
  
  @impl true
  def validate_config(config) do
    required_keys = [:classification_model, :categories]
    
    case Enum.all?(required_keys, &Map.has_key?(config, &1)) do
      true -> {:ok, config}
      false -> {:error, "Missing required configuration keys"}
    end
  end
  
  @impl true
  def execute(input, config) do
    with {:ok, text} <- extract_text(input),
         {:ok, features} <- extract_features(text, config),
         {:ok, classification} <- classify_document(features, config),
         {:ok, enriched} <- enrich_classification(classification, input) do
      
      {:ok, Map.merge(input, %{
        classification: enriched,
        metadata: %{
          operator: "CustomClassificationOperator",
          version: "1.0",
          timestamp: DateTime.utc_now()
        }
      })}
    end
  end
  
  defp extract_features(text, config) do
    features = %{
      word_count: String.split(text) |> length(),
      contains_legal_terms: contains_legal_terms?(text),
      document_structure: analyze_structure(text),
      key_phrases: extract_key_phrases(text),
      industry_signals: detect_industry_signals(text, config.industry)
    }
    
    {:ok, features}
  end
  
  defp classify_document(features, config) do
    # Load pre-trained model
    model = load_model(config.classification_model)
    
    # Predict classification
    predictions = model.predict(features)
    
    # Apply business rules
    adjusted_predictions = apply_business_rules(predictions, features, config)
    
    {:ok, %{
      primary_category: hd(adjusted_predictions),
      all_categories: adjusted_predictions,
      confidence_scores: calculate_confidence(predictions),
      explanation: generate_explanation(features, predictions)
    }}
  end
  
  defp apply_business_rules(predictions, features, config) do
    # Example: Legal documents with certain terms must be classified as privileged
    if features.contains_legal_terms && 
       Enum.any?(features.key_phrases, &privileged_phrase?/1) do
      ["privileged_legal" | predictions]
      |> Enum.uniq()
      |> Enum.take(5)
    else
      predictions
    end
  end
end
```

## Integration Examples

### 7. Real-time Processing with WebSockets

```typescript
// Real-time document processing monitor
import { Socket, Channel } from 'phoenix';

class DocumentProcessingMonitor {
  private socket: Socket;
  private processingChannel: Channel;
  private caseChannels: Map<string, Channel> = new Map();
  
  constructor(token: string) {
    this.socket = new Socket('wss://api.ediscovery.com/socket', {
      params: { token }
    });
    
    this.socket.connect();
    this.setupGlobalChannel();
  }
  
  private setupGlobalChannel() {
    this.processingChannel = this.socket.channel('processing:global');
    
    this.processingChannel.on('job:started', (payload) => {
      console.log(`Processing started: ${payload.job_id}`);
      this.trackJob(payload.job_id);
    });
    
    this.processingChannel.join()
      .receive('ok', () => console.log('Connected to global processing channel'))
      .receive('error', (err) => console.error('Failed to connect:', err));
  }
  
  monitorCase(caseId: string, callbacks: {
    onDocumentUploaded?: (doc: any) => void;
    onDocumentProcessed?: (doc: any) => void;
    onError?: (error: any) => void;
  }) {
    const channel = this.socket.channel(`case:${caseId}`);
    
    if (callbacks.onDocumentUploaded) {
      channel.on('document:uploaded', callbacks.onDocumentUploaded);
    }
    
    if (callbacks.onDocumentProcessed) {
      channel.on('document:processed', callbacks.onDocumentProcessed);
    }
    
    if (callbacks.onError) {
      channel.on('processing:error', callbacks.onError);
    }
    
    // Real-time statistics
    channel.on('stats:updated', (stats) => {
      this.updateDashboard(caseId, stats);
    });
    
    channel.join()
      .receive('ok', () => {
        console.log(`Monitoring case: ${caseId}`);
        this.caseChannels.set(caseId, channel);
      });
    
    return () => {
      channel.leave();
      this.caseChannels.delete(caseId);
    };
  }
  
  private trackJob(jobId: string) {
    const jobChannel = this.socket.channel(`processing:job:${jobId}`);
    
    jobChannel.on('progress', (update) => {
      const percentage = (update.completed / update.total) * 100;
      console.log(`Job ${jobId}: ${percentage.toFixed(1)}% complete`);
      
      // Update UI
      this.updateProgressBar(jobId, percentage);
    });
    
    jobChannel.on('document:complete', (doc) => {
      console.log(`Document processed: ${doc.filename}`);
      this.addToCompletedList(doc);
    });
    
    jobChannel.on('job:complete', (summary) => {
      console.log(`Job ${jobId} complete:`, summary);
      jobChannel.leave();
    });
    
    jobChannel.join();
  }
  
  // UI update methods
  private updateDashboard(caseId: string, stats: any) {
    document.getElementById(`case-${caseId}-stats`).innerHTML = `
      <div class="stats-grid">
        <div class="stat">
          <span class="label">Total Documents</span>
          <span class="value">${stats.total_documents}</span>
        </div>
        <div class="stat">
          <span class="label">Processed</span>
          <span class="value">${stats.processed_documents}</span>
        </div>
        <div class="stat">
          <span class="label">Privileged</span>
          <span class="value">${stats.privileged_count}</span>
        </div>
        <div class="stat">
          <span class="label">Processing Rate</span>
          <span class="value">${stats.docs_per_minute} docs/min</span>
        </div>
      </div>
    `;
  }
  
  private updateProgressBar(jobId: string, percentage: number) {
    const progressBar = document.getElementById(`progress-${jobId}`);
    if (progressBar) {
      progressBar.style.width = `${percentage}%`;
      progressBar.textContent = `${percentage.toFixed(1)}%`;
    }
  }
  
  private addToCompletedList(doc: any) {
    const list = document.getElementById('completed-documents');
    const item = document.createElement('li');
    item.className = 'document-item';
    item.innerHTML = `
      <span class="filename">${doc.filename}</span>
      <span class="status ${doc.privilege_status}">${doc.privilege_status}</span>
      <span class="entities">${doc.entity_count} entities</span>
    `;
    list.prepend(item);
  }
}

// Usage
const monitor = new DocumentProcessingMonitor(authToken);

// Monitor specific case
const unsubscribe = monitor.monitorCase('case_123', {
  onDocumentUploaded: (doc) => {
    showNotification(`New document: ${doc.filename}`);
  },
  onDocumentProcessed: (doc) => {
    if (doc.privilege_status === 'privileged') {
      highlightPrivilegedDocument(doc);
    }
  },
  onError: (error) => {
    showErrorAlert(error.message);
  }
});

// Later: stop monitoring
unsubscribe();
```

### 8. Hypergraph Traversal

```python
# Example: Find all related documents through hypergraph
async def explore_document_network(document_id: str, max_depth: int = 3):
    client = Client(api_key="your-api-key")
    
    # Get document's hypergraph node
    node = await client.hypergraph.get_node(document_id)
    
    # Find all connected documents through various relationships
    related_docs = await client.hypergraph.traverse(
        start_node=node,
        traversal_spec={
            "max_depth": max_depth,
            "relationships": [
                "same_thread",      # Email threads
                "references",       # Document references
                "shared_entities",  # Common entities
                "privilege_group",  # Same privilege classification
                "temporal_proximity" # Close in time
            ],
            "filters": {
                "node_type": "document",
                "min_relationship_strength": 0.7
            }
        }
    )
    
    # Build relationship graph
    graph = {}
    for path in related_docs.paths:
        for i, node in enumerate(path.nodes[:-1]):
            next_node = path.nodes[i + 1]
            edge = path.edges[i]
            
            if node.id not in graph:
                graph[node.id] = []
            
            graph[node.id].append({
                "target": next_node.id,
                "relationship": edge.type,
                "strength": edge.weight,
                "properties": edge.properties
            })
    
    # Analyze document clusters
    clusters = await client.hypergraph.find_clusters(
        nodes=[doc.id for doc in related_docs.nodes],
        algorithm="louvain",
        min_cluster_size=3
    )
    
    # Generate insights
    insights = {
        "total_related_documents": len(related_docs.nodes),
        "relationship_types": count_relationship_types(related_docs.edges),
        "document_clusters": [
            {
                "cluster_id": cluster.id,
                "size": len(cluster.nodes),
                "key_entities": extract_key_entities(cluster),
                "common_themes": analyze_themes(cluster),
                "date_range": get_date_range(cluster)
            }
            for cluster in clusters
        ],
        "key_documents": identify_central_documents(graph),
        "timeline": build_timeline(related_docs.nodes)
    }
    
    return insights

# Usage
insights = await explore_document_network("doc_12345", max_depth=3)
print(f"Found {insights['total_related_documents']} related documents")
print(f"Identified {len(insights['document_clusters'])} document clusters")

for cluster in insights['document_clusters']:
    print(f"\nCluster {cluster['cluster_id']}:")
    print(f"  Size: {cluster['size']} documents")
    print(f"  Key entities: {', '.join(cluster['key_entities'][:5])}")
    print(f"  Date range: {cluster['date_range']['start']} to {cluster['date_range']['end']}")
```

## Analytics Examples

### 9. Case Analytics Dashboard

```python
# Generate comprehensive case analytics
async def generate_case_analytics(case_id: str, date_range: Optional[DateRange] = None):
    client = Client(api_key="your-api-key")
    
    # Fetch case data
    case = await client.cases.get(case_id)
    
    # Document statistics
    doc_stats = await client.analytics.document_statistics(
        case_id=case_id,
        date_range=date_range,
        metrics=[
            "total_documents",
            "processed_documents",
            "processing_status_breakdown",
            "document_types",
            "file_sizes",
            "processing_times"
        ]
    )
    
    # Entity analytics
    entity_stats = await client.analytics.entity_analysis(
        case_id=case_id,
        entity_types=["person", "organization", "location"],
        metrics=[
            "unique_entities",
            "entity_frequency",
            "entity_relationships",
            "entity_timeline",
            "key_players"
        ]
    )
    
    # Privilege analysis
    privilege_stats = await client.analytics.privilege_analysis(
        case_id=case_id,
        breakdown_by=["privilege_type", "reviewer", "confidence_level"],
        include_trends=True
    )
    
    # Communication patterns
    comm_analysis = await client.analytics.communication_patterns(
        case_id=case_id,
        analysis_types=[
            "email_threads",
            "communication_frequency",
            "response_times",
            "sentiment_analysis",
            "key_topics"
        ]
    )
    
    # Cost analysis
    cost_analysis = await client.analytics.cost_breakdown(
        case_id=case_id,
        include=[
            "api_usage",
            "storage_costs",
            "processing_time",
            "human_review_hours"
        ]
    )
    
    # Generate report
    report = {
        "case_summary": {
            "case_id": case.id,
            "case_name": case.name,
            "date_range": date_range or {"start": case.created_at, "end": "now"},
            "generated_at": datetime.utcnow().isoformat()
        },
        "document_metrics": {
            "total": doc_stats.total_documents,
            "processed": doc_stats.processed_documents,
            "processing_rate": f"{doc_stats.avg_processing_rate} docs/hour",
            "by_type": doc_stats.document_types,
            "by_status": doc_stats.processing_status_breakdown
        },
        "entity_insights": {
            "total_unique_entities": entity_stats.unique_entities,
            "key_people": entity_stats.key_players[:10],
            "organization_network": entity_stats.organization_relationships,
            "geographic_distribution": entity_stats.location_analysis
        },
        "privilege_summary": {
            "privileged_documents": privilege_stats.privileged_count,
            "privilege_rate": f"{privilege_stats.privilege_percentage}%",
            "by_type": privilege_stats.privilege_type_breakdown,
            "confidence_distribution": privilege_stats.confidence_histogram
        },
        "communication_insights": {
            "total_threads": comm_analysis.thread_count,
            "active_participants": comm_analysis.unique_participants,
            "peak_activity": comm_analysis.peak_periods,
            "sentiment_summary": comm_analysis.overall_sentiment,
            "trending_topics": comm_analysis.top_topics[:20]
        },
        "cost_summary": {
            "total_cost": cost_analysis.total_cost,
            "cost_breakdown": cost_analysis.breakdown,
            "projected_total": cost_analysis.projected_final_cost
        }
    }
    
    # Generate visualizations
    charts = await generate_analytics_charts(report)
    
    # Export report
    pdf_url = await export_analytics_report(report, charts, format="pdf")
    
    return {
        "report": report,
        "charts": charts,
        "export_url": pdf_url
    }

# Usage
analytics = await generate_case_analytics(
    case_id="case_123",
    date_range={"start": "2023-01-01", "end": "2023-12-31"}
)

print(f"Total documents: {analytics['report']['document_metrics']['total']}")
print(f"Key people: {', '.join(p['name'] for p in analytics['report']['entity_insights']['key_people'][:5])}")
print(f"Privilege rate: {analytics['report']['privilege_summary']['privilege_rate']}")
print(f"Report URL: {analytics['export_url']}")
```

### 10. Custom Compliance Report

```python
# Generate GDPR compliance report for data subject request
async def generate_gdpr_report(data_subject_email: str):
    client = Client(api_key="your-api-key")
    
    # Find all documents mentioning the data subject
    documents = await client.search.documents(
        query=f'"{data_subject_email}"',
        include_all_cases=True,
        filters={
            "entity_email": data_subject_email
        }
    )
    
    # Analyze personal data found
    personal_data_analysis = await client.compliance.analyze_personal_data(
        documents=[doc.id for doc in documents.results],
        data_subject=data_subject_email
    )
    
    # Generate GDPR-compliant report
    gdpr_report = {
        "report_metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "data_subject": data_subject_email,
            "request_type": "access_request",
            "report_id": str(uuid.uuid4())
        },
        
        "data_summary": {
            "total_documents_containing_data": len(documents.results),
            "cases_involved": list(set(doc.case_id for doc in documents.results)),
            "date_range": {
                "earliest": min(doc.created_at for doc in documents.results),
                "latest": max(doc.created_at for doc in documents.results)
            }
        },
        
        "personal_data_found": {
            "email_addresses": personal_data_analysis.email_addresses,
            "phone_numbers": personal_data_analysis.phone_numbers,
            "physical_addresses": personal_data_analysis.physical_addresses,
            "identification_numbers": personal_data_analysis.identification_numbers,
            "financial_information": personal_data_analysis.financial_information,
            "health_information": personal_data_analysis.health_information
        },
        
        "data_usage": {
            "purposes": [
                "Legal proceedings - litigation support",
                "Compliance with legal obligations",
                "Legitimate interests - legal discovery"
            ],
            "legal_basis": "Legitimate interests under GDPR Article 6(1)(f)",
            "retention_period": "7 years from case closure",
            "data_sharing": {
                "internal": ["Legal team", "Compliance team"],
                "external": ["Court-appointed parties", "Opposing counsel (under protective order)"]
            }
        },
        
        "documents_detail": [
            {
                "document_id": doc.id,
                "filename": doc.filename,
                "case": doc.case_name,
                "personal_data_types": analyze_personal_data_in_doc(doc),
                "context": extract_context(doc, data_subject_email),
                "can_be_redacted": doc.privilege_status != "privileged",
                "retention_status": doc.retention_status
            }
            for doc in documents.results[:100]  # Limit to first 100 for readability
        ],
        
        "rights_information": {
            "right_to_access": "This report fulfills your access request",
            "right_to_rectification": "Contact legal@company.com to request corrections",
            "right_to_erasure": "Subject to legal hold obligations",
            "right_to_portability": "Data available in machine-readable format upon request",
            "right_to_object": "You may object to processing for legitimate interests"
        }
    }
    
    # Generate PDF report
    pdf_report = await client.compliance.generate_pdf_report(
        gdpr_report,
        template="gdpr_access_request",
        include_watermark=True
    )
    
    # Log the access request
    await client.compliance.log_data_subject_request(
        data_subject=data_subject_email,
        request_type="access",
        report_id=gdpr_report["report_metadata"]["report_id"],
        fulfilled_at=datetime.utcnow()
    )
    
    return {
        "report": gdpr_report,
        "pdf_url": pdf_report.url,
        "report_id": gdpr_report["report_metadata"]["report_id"]
    }

# Usage
gdpr_report = await generate_gdpr_report("john.doe@example.com")
print(f"Found personal data in {gdpr_report['report']['data_summary']['total_documents_containing_data']} documents")
print(f"Report available at: {gdpr_report['pdf_url']}")
```

## Testing Examples

### 11. Integration Testing

```python
# pytest example for testing document processing
import pytest
from unittest.mock import Mock, patch
import asyncio

@pytest.fixture
async def client():
    """Create test client"""
    return Client(api_key="test-api-key", base_url="http://localhost:4000")

@pytest.fixture
def sample_document():
    """Sample document for testing"""
    return {
        "filename": "test_contract.pdf",
        "content": "This is a test contract between Acme Corp and Beta Inc...",
        "metadata": {
            "author": "legal@acme.com",
            "created": "2024-01-15"
        }
    }

@pytest.mark.asyncio
async def test_document_processing_workflow(client, sample_document):
    """Test complete document processing workflow"""
    
    # Upload document
    upload_result = await client.documents.upload(
        file=sample_document,
        case_id="test_case_123"
    )
    
    assert upload_result.status == "uploaded"
    assert upload_result.document_id is not None
    
    # Start processing
    processing_job = await client.processing.start(
        document_ids=[upload_result.document_id],
        workflow="standard_legal_review"
    )
    
    assert processing_job.status == "queued"
    
    # Wait for completion (with timeout)
    completed = await processing_job.wait_for_completion(timeout=300)
    
    assert completed.status == "completed"
    assert len(completed.results) == 1
    
    # Verify results
    result = completed.results[0]
    assert result.document_id == upload_result.document_id
    assert "entities" in result
    assert "summary" in result
    assert "privilege_analysis" in result
    
    # Verify entity extraction
    entities = result["entities"]
    assert any(e["text"] == "Acme Corp" for e in entities)
    assert any(e["text"] == "Beta Inc" for e in entities)
    
    # Verify privilege analysis
    privilege = result["privilege_analysis"]
    assert "is_privileged" in privilege
    assert "confidence" in privilege
    assert privilege["confidence"] >= 0.0 and privilege["confidence"] <= 1.0

@pytest.mark.asyncio
async def test_search_functionality(client):
    """Test search with various filters"""
    
    # Perform search
    results = await client.search.documents(
        query="contract breach",
        filters={
            "case_ids": ["test_case_123"],
            "document_types": ["contract", "email"]
        },
        page=1,
        per_page=10
    )
    
    assert results.total >= 0
    assert len(results.documents) <= 10
    
    # Verify search results structure
    if results.documents:
        doc = results.documents[0]
        assert "id" in doc
        assert "filename" in doc
        assert "relevance_score" in doc
        assert doc.relevance_score >= 0.0 and doc.relevance_score <= 1.0

@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling for invalid requests"""
    
    # Test invalid document ID
    with pytest.raises(DocumentNotFoundError):
        await client.documents.get("invalid_doc_id")
    
    # Test invalid workflow
    with pytest.raises(WorkflowNotFoundError):
        await client.processing.start(
            document_ids=["doc_123"],
            workflow="non_existent_workflow"
        )
    
    # Test rate limiting
    tasks = []
    for _ in range(150):  # Exceed rate limit
        tasks.append(client.documents.list())
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Should have some rate limit errors
    rate_limit_errors = [r for r in results if isinstance(r, RateLimitError)]
    assert len(rate_limit_errors) > 0

@pytest.mark.asyncio
async def test_websocket_updates(client):
    """Test real-time updates via WebSocket"""
    
    updates = []
    
    # Subscribe to updates
    async def handle_update(update):
        updates.append(update)
    
    await client.subscribe_to_case("test_case_123", handle_update)
    
    # Trigger an action that should generate updates
    await client.documents.upload(
        file={"filename": "test.pdf", "content": "test content"},
        case_id="test_case_123"
    )
    
    # Wait for updates
    await asyncio.sleep(2)
    
    # Verify we received updates
    assert len(updates) > 0
    assert any(u["type"] == "document:uploaded" for u in updates)
```

## Performance Optimization Examples

### 12. Batch Processing Optimization

```python
# Optimized batch processing with connection pooling and caching
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aioredis
from functools import lru_cache

class OptimizedBatchProcessor:
    def __init__(self, api_key: str, max_workers: int = 10):
        self.client = Client(api_key=api_key)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.redis = None
        self.processing_cache = {}
        
    async def initialize(self):
        """Initialize connections and caches"""
        self.redis = await aioredis.create_redis_pool('redis://localhost')
        
    async def process_large_batch(self, document_files: List[Path], case_id: str):
        """Process large batch of documents efficiently"""
        
        # Split into chunks for parallel processing
        chunk_size = 50
        chunks = [document_files[i:i + chunk_size] 
                 for i in range(0, len(document_files), chunk_size)]
        
        # Process chunks in parallel
        tasks = []
        for i, chunk in enumerate(chunks):
            task = self.process_chunk(chunk, case_id, chunk_id=i)
            tasks.append(task)
        
        # Use semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(5)
        
        async def process_with_limit(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(*[process_with_limit(task) for task in tasks])
        
        # Aggregate results
        all_results = []
        failed_documents = []
        
        for chunk_result in results:
            all_results.extend(chunk_result["successful"])
            failed_documents.extend(chunk_result["failed"])
        
        # Generate summary report
        summary = {
            "total_documents": len(document_files),
            "successful": len(all_results),
            "failed": len(failed_documents),
            "processing_time": sum(r.get("processing_time", 0) for r in all_results),
            "average_time_per_doc": sum(r.get("processing_time", 0) for r in all_results) / len(all_results) if all_results else 0,
            "failed_documents": failed_documents
        }
        
        return summary
    
    async def process_chunk(self, documents: List[Path], case_id: str, chunk_id: int):
        """Process a chunk of documents"""
        
        successful = []
        failed = []
        
        # Check cache for already processed documents
        cached_results = await self.check_cache_batch([doc.name for doc in documents])
        
        # Process uncached documents
        to_process = []
        for doc in documents:
            if doc.name not in cached_results:
                to_process.append(doc)
            else:
                successful.append(cached_results[doc.name])
        
        if to_process:
            # Upload batch
            upload_results = await self.batch_upload(to_process, case_id)
            
            # Process with optimized workflow
            processing_results = await self.batch_process(
                [r["document_id"] for r in upload_results if r["status"] == "success"],
                workflow="optimized_batch_processing"
            )
            
            # Cache results
            await self.cache_results(processing_results)
            
            successful.extend(processing_results)
        
        return {
            "chunk_id": chunk_id,
            "successful": successful,
            "failed": failed
        }
    
    async def batch_upload(self, files: List[Path], case_id: str):
        """Optimized batch upload with streaming"""
        
        # Create multipart upload session
        session = await self.client.documents.create_batch_upload_session(
            case_id=case_id,
            total_files=len(files)
        )
        
        # Upload files in parallel with streaming
        upload_tasks = []
        for file in files:
            task = self.stream_upload_file(session.session_id, file)
            upload_tasks.append(task)
        
        results = await asyncio.gather(*upload_tasks, return_exceptions=True)
        
        # Finalize upload session
        await session.finalize()
        
        return results
    
    async def stream_upload_file(self, session_id: str, file_path: Path):
        """Stream upload large files"""
        
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        
        async with aiofiles.open(file_path, 'rb') as f:
            chunk_number = 0
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                
                await self.client.documents.upload_chunk(
                    session_id=session_id,
                    filename=file_path.name,
                    chunk_number=chunk_number,
                    chunk_data=chunk
                )
                
                chunk_number += 1
        
        return {
            "filename": file_path.name,
            "status": "success",
            "chunks": chunk_number
        }
    
    @lru_cache(maxsize=1000)
    async def check_cache_batch(self, document_names: List[str]):
        """Check Redis cache for processed documents"""
        
        if not self.redis:
            return {}
        
        # Use Redis pipeline for batch get
        pipe = self.redis.pipeline()
        for name in document_names:
            pipe.get(f"processed:{name}")
        
        results = await pipe.execute()
        
        cached = {}
        for name, result in zip(document_names, results):
            if result:
                cached[name] = json.loads(result)
        
        return cached
    
    async def cache_results(self, results: List[Dict]):
        """Cache processing results"""
        
        if not self.redis:
            return
        
        pipe = self.redis.pipeline()
        for result in results:
            key = f"processed:{result['filename']}"
            value = json.dumps(result)
            pipe.setex(key, 3600, value)  # 1 hour TTL
        
        await pipe.execute()

# Usage
processor = OptimizedBatchProcessor(api_key="your-api-key", max_workers=20)
await processor.initialize()

# Process large batch
documents = list(Path("/data/documents").glob("*.pdf"))
results = await processor.process_large_batch(documents, case_id="case_123")

print(f"Processed {results['successful']} of {results['total_documents']} documents")
print(f"Average processing time: {results['average_time_per_doc']:.2f} seconds per document")

if results['failed_documents']:
    print(f"Failed documents: {results['failed_documents']}")
```

## Next Steps

- Review [API Documentation](/api/rest) for detailed endpoint information
- Check [Deployment Guide](/deployment/production) for running these examples in production
- See [Support](/support) for troubleshooting and best practices