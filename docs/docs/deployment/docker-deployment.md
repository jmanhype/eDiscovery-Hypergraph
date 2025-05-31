---
id: docker-deployment
title: Docker Deployment
sidebar_label: Docker
---

# Docker Deployment

This guide covers deploying the eDiscovery Hypergraph platform using Docker and Docker Compose, from development environments to production-ready configurations.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended for production)
- 50GB available disk space

## Quick Start

### Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/ediscovery-hypergraph.git
cd ediscovery-hypergraph

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Required: OPENAI_API_KEY
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
open http://localhost:3000
```

### Service Endpoints

- Frontend: http://localhost:3000
- Phoenix API: http://localhost:4000
- Python API: http://localhost:8001
- GraphQL Playground: http://localhost:4000/graphiql
- MongoDB: mongodb://localhost:27017
- NATS: nats://localhost:4222

## Docker Images

### Base Images

```dockerfile
# Elixir/Phoenix Base
FROM elixir:1.14-alpine AS elixir-base

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    git \
    python3 \
    npm \
    postgresql-client

# Install hex and rebar
RUN mix local.hex --force && \
    mix local.rebar --force

# Python AI Service Base
FROM python:3.11-slim AS python-base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Frontend Base
FROM node:18-alpine AS frontend-base

# Install dependencies
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++
```

### Multi-Stage Build

```dockerfile
# Complete Dockerfile for Phoenix service
FROM elixir:1.14-alpine AS builder

# Install build dependencies
RUN apk add --no-cache build-base git python3 npm

# Prepare build dir
WORKDIR /app

# Install hex + rebar
RUN mix local.hex --force && \
    mix local.rebar --force

# Set build ENV
ENV MIX_ENV=prod

# Install mix dependencies
COPY mix.exs mix.lock ./
COPY config config
RUN mix deps.get --only $MIX_ENV
RUN mix deps.compile

# Build assets
COPY assets/package.json assets/package-lock.json ./assets/
RUN npm --prefix ./assets ci --progress=false --no-audit --loglevel=error

COPY priv priv
COPY assets assets
RUN npm run --prefix ./assets deploy
RUN mix phx.digest

# Compile and build release
COPY lib lib
RUN mix compile

# Build release
COPY rel rel
RUN mix release

# Start a new build stage for runtime
FROM alpine:3.18 AS runtime

RUN apk add --no-cache openssl ncurses-libs libstdc++

WORKDIR /app

RUN chown nobody:nobody /app

USER nobody:nobody

COPY --from=builder --chown=nobody:nobody /app/_build/prod/rel/a2a_agent ./

ENV HOME=/app

EXPOSE 4000

CMD ["bin/a2a_agent", "start"]
```

## Docker Compose Configuration

### Complete Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  # MongoDB Database
  mongodb:
    image: mongo:6.0
    container_name: ediscovery-mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD:-changeme}
      MONGO_INITDB_DATABASE: ${MONGO_DATABASE:-ediscovery}
    volumes:
      - mongodb_data:/data/db
      - ./init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
    networks:
      - ediscovery-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  # NATS Message Broker
  nats:
    image: nats:2.10-alpine
    container_name: ediscovery-nats
    restart: unless-stopped
    ports:
      - "4222:4222"
      - "8222:8222"
    command: ["--js", "--sd", "/data", "-m", "8222"]
    volumes:
      - nats_data:/data
    networks:
      - ediscovery-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: ediscovery-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - ediscovery-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Elasticsearch (Optional - for advanced search)
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: ediscovery-elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - ediscovery-network
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Phoenix/Elixir Backend
  phoenix:
    build:
      context: .
      dockerfile: Dockerfile.phoenix
      args:
        MIX_ENV: ${MIX_ENV:-prod}
    container_name: ediscovery-phoenix
    restart: unless-stopped
    ports:
      - "4000:4000"
    environment:
      DATABASE_URL: ${DATABASE_URL:-ecto://postgres:postgres@postgres/ediscovery}
      MONGODB_URL: ${MONGODB_URL:-mongodb://admin:changeme@mongodb:27017/ediscovery?authSource=admin}
      NATS_URL: ${NATS_URL:-nats://nats:4222}
      REDIS_URL: ${REDIS_URL:-redis://redis:6379}
      SECRET_KEY_BASE: ${SECRET_KEY_BASE}
      PHX_HOST: ${PHX_HOST:-localhost}
      PORT: 4000
    depends_on:
      mongodb:
        condition: service_healthy
      nats:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - ediscovery-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:4000/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Python AI Service
  python-ai:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ediscovery-python
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      MONGODB_URL: ${MONGODB_URL:-mongodb://admin:changeme@mongodb:27017/ediscovery?authSource=admin}
      REDIS_URL: ${REDIS_URL:-redis://redis:6379}
      NATS_URL: ${NATS_URL:-nats://nats:4222}
      ENVIRONMENT: ${ENVIRONMENT:-production}
    depends_on:
      mongodb:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - ediscovery-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        REACT_APP_API_URL: ${REACT_APP_API_URL:-http://localhost:4000/api}
        REACT_APP_GRAPHQL_URL: ${REACT_APP_GRAPHQL_URL:-http://localhost:4000/graphql}
        REACT_APP_WS_URL: ${REACT_APP_WS_URL:-ws://localhost:4000/socket}
    container_name: ediscovery-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - phoenix
    networks:
      - ediscovery-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: ediscovery-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_cache:/var/cache/nginx
    depends_on:
      - phoenix
      - python-ai
      - frontend
    networks:
      - ediscovery-network

networks:
  ediscovery-network:
    driver: bridge

volumes:
  mongodb_data:
  nats_data:
  redis_data:
  elasticsearch_data:
  nginx_cache:
```

### Environment Configuration

```bash
# .env file
# Application
ENVIRONMENT=production
APP_NAME=eDiscovery-Hypergraph

# Security
SECRET_KEY_BASE=your-secret-key-base-min-64-chars
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key

# Database
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=secure-password
MONGO_DATABASE=ediscovery
MONGODB_URL=mongodb://admin:secure-password@mongodb:27017/ediscovery?authSource=admin

# Cache
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=redis-password

# Message Queue
NATS_URL=nats://nats:4222

# AI Service
OPENAI_API_KEY=your-openai-api-key
AI_MODEL=gpt-4-turbo
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_GRAPHQL_URL=https://api.yourdomain.com/graphql
REACT_APP_WS_URL=wss://api.yourdomain.com/socket

# Email (Optional)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-sendgrid-api-key
SMTP_FROM=noreply@yourdomain.com

# Monitoring (Optional)
SENTRY_DSN=https://your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-new-relic-key
```

## Production Optimizations

### 1. Multi-Stage Builds

```dockerfile
# Optimized Python service Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy application code
COPY . .

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Gunicorn configuration
ENV PYTHONUNBUFFERED=1
ENV WORKERS=4
ENV WORKER_CLASS=uvicorn.workers.UvicornWorker
ENV BIND=0.0.0.0:8001

EXPOSE 8001

CMD ["gunicorn", "server:app", \
     "--workers", "${WORKERS}", \
     "--worker-class", "${WORKER_CLASS}", \
     "--bind", "${BIND}", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "120"]
```

### 2. Resource Limits

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  phoenix:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    environment:
      POOL_SIZE: 20
      BEAM_SCHEDULERS: 4
      ERL_MAX_PORTS: 4096

  python-ai:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    environment:
      WORKERS: 8
      WORKER_CONNECTIONS: 1000
      MAX_REQUESTS: 1000
      MAX_REQUESTS_JITTER: 100

  mongodb:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
    command: mongod --wiredTigerCacheSizeGB 4
```

### 3. Health Checks and Monitoring

```yaml
# Monitoring stack addition
  prometheus:
    image: prom/prometheus:latest
    container_name: ediscovery-prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    networks:
      - ediscovery-network

  grafana:
    image: grafana/grafana:latest
    container_name: ediscovery-grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3001:3000"
    networks:
      - ediscovery-network

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: ediscovery-cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    devices:
      - /dev/kmsg
    networks:
      - ediscovery-network
```

## Deployment Commands

### Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Execute commands in container
docker-compose exec phoenix mix ecto.migrate
docker-compose exec python-ai python manage.py migrate

# Rebuild specific service
docker-compose build phoenix
docker-compose up -d phoenix

# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Production

```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Rolling update
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps phoenix

# Backup volumes
docker run --rm -v ediscovery_mongodb_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/mongodb-backup-$(date +%Y%m%d).tar.gz -C /data .

# Scale service
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --scale python-ai=3

# View resource usage
docker stats

# Health check status
docker-compose ps
```

## Docker Swarm Deployment

### Initialize Swarm

```bash
# Initialize swarm mode
docker swarm init --advertise-addr <MANAGER-IP>

# Add worker nodes
docker swarm join --token <TOKEN> <MANAGER-IP>:2377

# Deploy stack
docker stack deploy -c docker-stack.yml ediscovery
```

### Stack Configuration

```yaml
# docker-stack.yml
version: '3.8'

services:
  phoenix:
    image: registry.yourdomain.com/ediscovery/phoenix:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: stop-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      placement:
        constraints:
          - node.role == worker
          - node.labels.type == app
    networks:
      - ediscovery-overlay
    secrets:
      - phoenix_secret_key
      - openai_api_key

  python-ai:
    image: registry.yourdomain.com/ediscovery/python:latest
    deploy:
      replicas: 5
      update_config:
        parallelism: 2
        delay: 10s
      placement:
        constraints:
          - node.labels.gpu == true
    networks:
      - ediscovery-overlay
    secrets:
      - openai_api_key

networks:
  ediscovery-overlay:
    driver: overlay
    attachable: true

secrets:
  phoenix_secret_key:
    external: true
  openai_api_key:
    external: true
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs phoenix

# Check container status
docker-compose ps

# Inspect container
docker inspect ediscovery-phoenix

# Check resource constraints
docker system df
docker system prune -a
```

#### 2. Database Connection Issues

```bash
# Test MongoDB connection
docker-compose exec mongodb mongosh \
  --host localhost \
  --username admin \
  --password changeme \
  --authenticationDatabase admin

# Check network
docker network inspect ediscovery-hypergraph_ediscovery-network

# Test connectivity between containers
docker-compose exec phoenix ping mongodb
```

#### 3. Performance Issues

```bash
# Monitor resource usage
docker stats

# Check container logs for errors
docker-compose logs --tail=100 -f

# Inspect volume usage
docker volume ls
docker volume inspect ediscovery-hypergraph_mongodb_data

# Check for memory issues
docker-compose exec phoenix cat /proc/meminfo
```

### Debug Mode

```yaml
# docker-compose.debug.yml
version: '3.8'

services:
  phoenix:
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
    stdin_open: true
    tty: true
    command: ["iex", "-S", "mix", "phx.server"]

  python-ai:
    environment:
      - PYTHONDEBUG=1
      - LOG_LEVEL=DEBUG
    command: ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "server:app", "--reload"]
    ports:
      - "5678:5678"  # Debug port
```

## Security Best Practices

### 1. Use Secrets Management

```bash
# Create secrets
echo "your-secret-key" | docker secret create phoenix_secret_key -
echo "your-openai-key" | docker secret create openai_api_key -

# Reference in compose
services:
  phoenix:
    secrets:
      - phoenix_secret_key
    environment:
      SECRET_KEY_BASE_FILE: /run/secrets/phoenix_secret_key
```

### 2. Network Isolation

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
  data:
    driver: bridge
    internal: true

services:
  nginx:
    networks:
      - frontend
      - backend
  
  phoenix:
    networks:
      - backend
      - data
  
  mongodb:
    networks:
      - data
```

### 3. Read-Only Filesystems

```yaml
services:
  frontend:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
      - /var/cache/nginx
```

### 4. User Permissions

```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Or in compose
services:
  phoenix:
    user: "1000:1000"
```

## Next Steps

- Review [Production Deployment](/deployment/production-deployment) for cloud deployments
- Check [Examples](/examples) for specific configurations
- See [Support](/support) for troubleshooting help