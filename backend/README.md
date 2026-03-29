# eDiscovery Backend API

FastAPI-based backend service for the eDiscovery Hypergraph Platform.

## Features

- **Document Processing**: AI-powered legal document analysis with OpenAI integration
- **User Authentication**: JWT-based authentication with role-based access control (RBAC)
- **Workflow Engine**: Async workflow execution with MongoDB persistence
- **Audit Logging**: Comprehensive audit trail for compliance
- **GraphQL API**: Alternative GraphQL interface alongside REST
- **Elasticsearch Integration**: Full-text search and aggregations
- **WebSocket Support**: Real-time updates for document processing

## Architecture

### Core Modules

- `server.py` - Main FastAPI application and route definitions
- `models.py` - Pydantic models for request/response validation
- `auth.py` - Authentication and authorization utilities
- `crud.py` - Database CRUD operations for core entities
- `workflow_crud.py` - Workflow-specific CRUD operations
- `workflow_engine.py` - Async workflow execution engine
- `audit_service.py` - Compliance and audit logging service
- `elasticsearch_service.py` - Full-text search integration
- `websocket_manager.py` - WebSocket connection management
- `graphql_schema.py` / `graphql_resolvers.py` - GraphQL API

## Setup

### Prerequisites

- Python 3.11+
- MongoDB 4.4+ (running locally or via Docker)
- OpenAI API key (for AI features)
- NATS Server (optional, for distributed processing)
- Elasticsearch 7.x+ (optional, for advanced search)

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required
SECRET_KEY=your-secure-random-secret-key-here-use-secrets-token-urlsafe-32
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGO_URL=mongodb://localhost:27017

# Optional
NATS_URL=nats://localhost:4222
ELASTICSEARCH_URL=http://localhost:9200
```

**IMPORTANT**: Never commit the `.env` file or use default/weak secret keys in production!

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- REST API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- GraphQL Playground: http://localhost:8000/graphql

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Authenticate and get JWT token
- `GET /api/auth/me` - Get current user info

### Documents
- `POST /api/documents` - Create document (auto-processes with AI)
- `GET /api/documents/{id}` - Get document details
- `PUT /api/documents/{id}` - Update document metadata
- `DELETE /api/documents/{id}` - Soft delete document
- `POST /api/documents/search` - Search with filters

### Cases
- `POST /api/cases` - Create new case/matter
- `GET /api/cases/{id}` - Get case details
- `GET /api/cases` - List cases

### Workflows
- `POST /api/workflows/definitions` - Create workflow definition
- `POST /api/workflows/instances` - Start workflow instance
- `GET /api/workflows/instances/{id}` - Get workflow status
- `POST /api/workflows/instances/search` - Search workflows

### eDiscovery Processing
- `POST /api/ediscovery/process` - Process emails through AI pipeline
- `GET /api/ediscovery/health` - Check service health

### Search (Elasticsearch)
- `POST /api/search/documents` - Full-text document search
- `POST /api/search/cases` - Search cases
- `POST /api/search/entities` - Search extracted entities
- `GET /api/search/suggest` - Autocomplete suggestions

### Audit & Compliance
- `GET /api/audit/logs` - Search audit logs (admin only)
- `GET /api/audit/compliance-report` - Generate compliance report
- `POST /api/audit/data-hold` - Create legal hold
- `GET /api/audit/retention-violations` - Check policy violations

## Security Features

### Authentication
- JWT-based token authentication
- Secure password hashing with bcrypt
- Account lockout after failed login attempts
- Automatic session expiration

### Authorization
- Role-based access control (RBAC)
- 5-tier role hierarchy: Admin > Attorney > Paralegal > Client > Viewer
- Case-level access restrictions
- Audit trail for all sensitive operations

### Security Best Practices
1. **Always set SECRET_KEY**: Use a cryptographically secure random key
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. **HTTPS in production**: Never transmit credentials over HTTP
3. **Environment variables**: Never commit secrets to version control
4. **Input validation**: All inputs validated via Pydantic models
5. **SQL injection prevention**: MongoDB parameterized queries
6. **Rate limiting**: Implement at reverse proxy level (nginx/Caddy)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend_test.py -v
```

## Development

### Adding New Endpoints

1. Define Pydantic models in `models.py`
2. Add CRUD operations in appropriate CRUD file
3. Create route handler in `server.py`
4. Add authentication/authorization decorators
5. Add audit logging for sensitive operations
6. Write tests

### Database Migrations

MongoDB is schemaless, but for data migrations:

```bash
# Create migration script
python scripts/migrate_data.py
```

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Troubleshooting

### Common Issues

**Issue**: `SECRET_KEY not set` warning
- **Solution**: Set `SECRET_KEY` environment variable to a secure random string

**Issue**: MongoDB connection refused
- **Solution**: Ensure MongoDB is running: `brew services start mongodb-community` or `docker run -d -p 27017:27017 mongo`

**Issue**: OpenAI API errors
- **Solution**: Verify `OPENAI_API_KEY` is set and valid. Check quota at platform.openai.com

**Issue**: NATS connection timeout
- **Solution**: NATS is optional. Server will fall back to direct API calls if NATS is unavailable.

## Performance Optimization

- **MongoDB indexes**: Created automatically on startup for common queries
- **Async processing**: All database and AI operations are async
- **Connection pooling**: Motor (async MongoDB driver) handles connection pooling
- **Caching**: Consider Redis for session/query caching in production

## Production Deployment

### Docker

```bash
docker build -t ediscovery-backend .
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e OPENAI_API_KEY=your-api-key \
  -e MONGO_URL=mongodb://mongo:27017 \
  ediscovery-backend
```

### Security Checklist
- [ ] Set strong SECRET_KEY
- [ ] Use HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Enable MongoDB authentication
- [ ] Configure CORS appropriately
- [ ] Set up log aggregation
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Backup strategy for MongoDB

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/jmanhype/eDiscovery-Hypergraph/issues
- Documentation: See `/docs` directory in project root
