---
id: support
title: Support
sidebar_label: Support
---

# Support

Welcome to the eDiscovery Hypergraph support page. Here you'll find resources to help you troubleshoot issues, get answers to common questions, and connect with our community.

## Getting Help

### 🚀 Quick Links

- **Status Page**: [status.ediscovery-hypergraph.com](https://status.ediscovery-hypergraph.com)
- **Community Slack**: [Join our Slack](https://slack.ediscovery-hypergraph.com)
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-org/ediscovery-hypergraph/issues)
- **Stack Overflow**: [Tag: ediscovery-hypergraph](https://stackoverflow.com/questions/tagged/ediscovery-hypergraph)

### 📧 Contact Support

- **Enterprise Support**: enterprise@ediscovery-hypergraph.com
- **Technical Support**: support@ediscovery-hypergraph.com
- **Sales Inquiries**: sales@ediscovery-hypergraph.com
- **Security Issues**: security@ediscovery-hypergraph.com

## Frequently Asked Questions (FAQ)

### General

<details>
<summary><strong>What is the eDiscovery Hypergraph platform?</strong></summary>

The eDiscovery Hypergraph platform is an AI-powered legal document processing system that combines advanced natural language processing with hypergraph data structures to provide superior document analysis, entity extraction, privilege detection, and relationship mapping for legal teams.

Key features include:
- AI-powered document analysis using OpenAI GPT-4
- Hypergraph-based relationship mapping
- Distributed workflow orchestration
- Real-time collaboration
- Enterprise-grade security and compliance

</details>

<details>
<summary><strong>What file formats are supported?</strong></summary>

We support a wide range of file formats commonly used in legal discovery:

**Documents**:
- PDF (.pdf)
- Microsoft Word (.doc, .docx)
- Plain Text (.txt)
- Rich Text Format (.rtf)
- OpenDocument Text (.odt)

**Emails**:
- Outlook (.msg, .pst)
- Email (.eml)
- MBOX (.mbox)

**Spreadsheets**:
- Microsoft Excel (.xls, .xlsx)
- CSV (.csv)
- OpenDocument Spreadsheet (.ods)

**Presentations**:
- Microsoft PowerPoint (.ppt, .pptx)
- OpenDocument Presentation (.odp)

**Images** (with OCR):
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tif, .tiff)
- GIF (.gif)

</details>

<details>
<summary><strong>How does pricing work?</strong></summary>

Our pricing is based on a combination of:

1. **Document Volume**: Number of documents processed
2. **Storage**: Amount of data stored
3. **AI Processing**: Complexity of AI operations used
4. **User Seats**: Number of active users

We offer three tiers:
- **Starter**: Up to 10,000 documents/month
- **Professional**: Up to 100,000 documents/month
- **Enterprise**: Unlimited with custom pricing

Contact sales@ediscovery-hypergraph.com for detailed pricing.

</details>

### Technical

<details>
<summary><strong>What are the system requirements?</strong></summary>

**For Cloud/SaaS Users**:
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Stable internet connection (minimum 10 Mbps recommended)
- JavaScript enabled

**For Self-Hosted Deployments**:

*Minimum Requirements*:
- 8 CPU cores
- 32 GB RAM
- 500 GB SSD storage
- Ubuntu 20.04+ or RHEL 8+
- Docker 20.10+
- Kubernetes 1.24+ (for production)

*Recommended Production*:
- 16+ CPU cores
- 64+ GB RAM
- 2+ TB SSD storage
- High-availability setup across multiple nodes

</details>

<details>
<summary><strong>How do I integrate with my existing systems?</strong></summary>

We provide multiple integration options:

**APIs**:
- REST API for simple integrations
- GraphQL API for complex queries
- WebSocket API for real-time updates

**SDKs**:
- Python SDK
- JavaScript/TypeScript SDK
- Java SDK (coming soon)
- .NET SDK (coming soon)

**Pre-built Integrations**:
- Relativity
- Concordance
- Microsoft 365
- Google Workspace
- Slack
- MS Teams

**Example Integration**:
```python
from ediscovery_hypergraph import Client

client = Client(api_key="your-api-key")

# Sync with external system
external_docs = fetch_from_relativity()
for doc in external_docs:
    client.documents.upload(
        file=doc.content,
        metadata=doc.metadata,
        case_id="case_123"
    )
```

</details>

<details>
<summary><strong>How is data encrypted?</strong></summary>

We implement multiple layers of encryption:

**At Rest**:
- AES-256 encryption for all stored data
- Encrypted database storage
- Encrypted file storage with unique keys per file
- Key management via HSM/KMS

**In Transit**:
- TLS 1.3 for all API communications
- Certificate pinning for mobile apps
- Perfect Forward Secrecy (PFS)
- Encrypted WebSocket connections

**Application Level**:
- Field-level encryption for sensitive data
- End-to-end encryption for privileged documents (optional)
- Zero-knowledge architecture available for highly sensitive deployments

</details>

### Processing and AI

<details>
<summary><strong>How accurate is the AI analysis?</strong></summary>

Our AI models achieve high accuracy rates:

- **Entity Extraction**: 94%+ precision, 92%+ recall
- **Privilege Detection**: 96%+ accuracy with human review
- **Document Classification**: 91%+ accuracy across categories
- **Summarization**: 89%+ ROUGE score

These metrics are based on legal document benchmarks. Accuracy can vary based on:
- Document quality and formatting
- Language and jurisdiction
- Domain-specific terminology
- Document types

We recommend human review for critical decisions and provide confidence scores for all AI predictions.

</details>

<details>
<summary><strong>How long does document processing take?</strong></summary>

Processing times depend on several factors:

**Typical Processing Times**:
- Text extraction: 1-5 seconds per document
- Entity extraction: 2-10 seconds per document
- Privilege classification: 3-15 seconds per document
- Full AI analysis: 10-30 seconds per document

**Factors Affecting Speed**:
- Document size and complexity
- Selected processing operations
- Current system load
- Priority level (enterprise customers can request priority processing)

**Batch Processing**:
- 1,000 documents: ~15-30 minutes
- 10,000 documents: ~2-4 hours
- 100,000 documents: ~20-40 hours

</details>

<details>
<summary><strong>Can I customize the AI models?</strong></summary>

Yes, we offer several customization options:

**Fine-tuning**:
- Train models on your specific document types
- Customize entity recognition for your industry
- Adjust privilege detection for your jurisdiction

**Custom Workflows**:
- Create custom operators
- Define business-specific rules
- Integrate your own ML models

**Example Custom Entity Training**:
```python
# Train custom entity recognizer
training_data = [
    {
        "text": "The ACME-2000 product violates patent US123456.",
        "entities": [
            {"start": 4, "end": 13, "label": "PRODUCT"},
            {"start": 36, "end": 44, "label": "PATENT_NUMBER"}
        ]
    }
]

model = client.ai.train_custom_ner(
    training_data=training_data,
    base_model="legal-ner-v2",
    entity_types=["PRODUCT", "PATENT_NUMBER"]
)
```

</details>

## Troubleshooting Guide

### Common Issues

#### Authentication Errors

**Problem**: "401 Unauthorized" errors

**Solutions**:
1. Verify your API key is correct
2. Check if the API key has expired
3. Ensure you're using the correct authentication header:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.ediscovery-hypergraph.com/v1/cases
   ```
4. For JWT auth, ensure the token hasn't expired

#### Upload Failures

**Problem**: Documents fail to upload

**Solutions**:
1. Check file size limits (default: 100MB per file)
2. Verify the file format is supported
3. Ensure you have sufficient storage quota
4. Check network connectivity and timeouts
5. For large files, use chunked upload:
   ```python
   client.documents.upload_large_file(
       file_path="large_document.pdf",
       chunk_size=5 * 1024 * 1024  # 5MB chunks
   )
   ```

#### Processing Errors

**Problem**: Documents stuck in "processing" status

**Solutions**:
1. Check the processing job status:
   ```python
   job = client.jobs.get(job_id)
   print(job.status, job.error)
   ```
2. Verify the document is not corrupted
3. Check if specific operations are failing
4. Review error logs in the dashboard
5. Retry with a simpler workflow

#### Search Performance

**Problem**: Searches are slow or timing out

**Solutions**:
1. Use more specific filters to reduce result set
2. Enable search result caching
3. Use pagination for large result sets
4. Consider using saved searches for complex queries
5. Optimize search queries:
   ```python
   # Instead of broad search
   results = client.search("contract")
   
   # Use specific search
   results = client.search(
       query="contract breach",
       filters={
           "date_range": {"start": "2023-01-01", "end": "2023-12-31"},
           "document_types": ["contract"],
           "case_ids": ["case_123"]
       },
       limit=50
   )
   ```

### Error Codes Reference

| Error Code | Description | Solution |
|------------|-------------|----------|
| `AUTH_001` | Invalid API key | Check your API key in settings |
| `AUTH_002` | Expired token | Refresh your authentication token |
| `DOC_001` | Unsupported file format | Convert to supported format |
| `DOC_002` | File too large | Use chunked upload or compress file |
| `PROC_001` | Processing timeout | Retry with smaller batch |
| `PROC_002` | AI service unavailable | Wait and retry, check status page |
| `SEARCH_001` | Query too complex | Simplify query or use filters |
| `RATE_001` | Rate limit exceeded | Implement backoff, upgrade plan |
| `STORAGE_001` | Storage quota exceeded | Delete old data or upgrade plan |

### Performance Optimization

#### Slow Dashboard Loading

1. **Clear browser cache**:
   - Chrome: Ctrl+Shift+Del (Cmd+Shift+Del on Mac)
   - Clear cached images and files

2. **Reduce data displayed**:
   ```javascript
   // Limit initial data load
   const cases = await client.cases.list({
     limit: 20,
     sort: 'updated_at',
     order: 'desc'
   });
   ```

3. **Enable progressive loading**:
   ```javascript
   // Load data as needed
   const lazyLoader = client.documents.createLazyLoader({
     pageSize: 50,
     prefetch: true
   });
   ```

#### API Response Times

1. **Use field selection**:
   ```graphql
   query GetDocuments {
     documents(first: 20) {
       edges {
         node {
           id
           filename
           # Only request needed fields
         }
       }
     }
   }
   ```

2. **Implement caching**:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_case_details(case_id):
       return client.cases.get(case_id)
   ```

3. **Batch operations**:
   ```python
   # Instead of individual requests
   for doc_id in document_ids:
       client.documents.get(doc_id)
   
   # Use batch endpoint
   documents = client.documents.get_batch(document_ids)
   ```

## Best Practices

### Security

1. **API Key Management**:
   - Rotate API keys regularly
   - Use environment variables, never commit keys
   - Implement key vault for production

2. **Access Control**:
   - Use principle of least privilege
   - Implement IP whitelisting for production
   - Enable 2FA for all user accounts

3. **Data Handling**:
   - Encrypt sensitive data before upload
   - Use secure deletion for removed documents
   - Implement audit logging for all access

### Performance

1. **Batch Processing**:
   - Process documents in batches of 50-100
   - Use parallel processing for large volumes
   - Implement retry logic with exponential backoff

2. **Caching Strategy**:
   - Cache frequently accessed data
   - Implement TTL for cache entries
   - Use Redis for distributed caching

3. **Resource Management**:
   - Monitor API usage and limits
   - Implement request pooling
   - Use connection pooling for database

### Workflow Design

1. **Modular Workflows**:
   - Create reusable operator components
   - Version control workflow definitions
   - Test workflows in staging first

2. **Error Handling**:
   - Implement comprehensive error handling
   - Use dead letter queues for failed jobs
   - Set up alerting for critical failures

3. **Monitoring**:
   - Track workflow execution metrics
   - Monitor operator performance
   - Set up dashboards for key metrics

## Community Resources

### Tutorials and Guides

- [Video: Getting Started with eDiscovery Hypergraph](https://youtube.com/...)
- [Blog: Best Practices for Large-Scale Document Processing](https://blog.ediscovery-hypergraph.com/...)
- [Webinar: AI in Legal Discovery](https://webinars.ediscovery-hypergraph.com/...)
- [Course: Advanced Workflow Design](https://learn.ediscovery-hypergraph.com/...)

### Sample Projects

- [GitHub: Example Integrations](https://github.com/your-org/ediscovery-examples)
- [GitHub: Custom Operators Library](https://github.com/your-org/custom-operators)
- [GitHub: Workflow Templates](https://github.com/your-org/workflow-templates)

### Community Contributions

We welcome contributions! See our [Contributing Guide](https://github.com/your-org/ediscovery-hypergraph/CONTRIBUTING.md) for:
- Code contribution guidelines
- Documentation improvements
- Bug reporting best practices
- Feature request process

## Professional Services

### Training

We offer comprehensive training programs:

- **Basic Training** (1 day): Platform overview and basic usage
- **Advanced Training** (3 days): Workflow design and customization
- **Developer Training** (5 days): API integration and custom development
- **Administrator Training** (2 days): Deployment and maintenance

### Consulting

Our professional services team can help with:

- Custom workflow development
- System integration
- Performance optimization
- Compliance configuration
- Migration from other platforms

### Support Plans

| Feature | Community | Professional | Enterprise |
|---------|-----------|--------------|------------|
| Documentation | ✓ | ✓ | ✓ |
| Community Forum | ✓ | ✓ | ✓ |
| Email Support | - | ✓ | ✓ |
| Phone Support | - | Business hours | 24/7 |
| Response Time | - | 24 hours | 1 hour |
| Dedicated Account Manager | - | - | ✓ |
| Custom Training | - | - | ✓ |
| SLA | - | 99.5% | 99.9% |

## Feedback

We value your feedback! Help us improve:

- **Feature Requests**: [Feature Request Form](https://feedback.ediscovery-hypergraph.com)
- **Bug Reports**: [GitHub Issues](https://github.com/your-org/ediscovery-hypergraph/issues)
- **Documentation**: [Docs Feedback](https://github.com/your-org/ediscovery-hypergraph-docs/issues)
- **General Feedback**: feedback@ediscovery-hypergraph.com

## Stay Updated

- **Blog**: [blog.ediscovery-hypergraph.com](https://blog.ediscovery-hypergraph.com)
- **Twitter**: [@eDiscoveryHG](https://twitter.com/eDiscoveryHG)
- **LinkedIn**: [eDiscovery Hypergraph](https://linkedin.com/company/ediscovery-hypergraph)
- **Newsletter**: [Subscribe for updates](https://ediscovery-hypergraph.com/newsletter)
- **Changelog**: [Latest releases and updates](https://docs.ediscovery-hypergraph.com/changelog)

---

**Need immediate assistance?** Our enterprise support team is available 24/7 at enterprise@ediscovery-hypergraph.com or +1-800-EDISCOV.