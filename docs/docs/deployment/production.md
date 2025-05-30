---
id: production-deployment
title: Production Deployment
sidebar_label: Production
---

# Production Deployment

This guide covers deploying the eDiscovery Hypergraph platform to production environments, including cloud providers, security hardening, monitoring, and scaling strategies.

## Infrastructure Requirements

### Minimum Production Requirements

| Component | CPU | Memory | Storage | Network |
|-----------|-----|---------|---------|---------|
| Load Balancer | 2 vCPU | 4 GB | 20 GB | 1 Gbps |
| Phoenix Nodes (x3) | 4 vCPU | 8 GB | 50 GB | 1 Gbps |
| Python AI Nodes (x3) | 8 vCPU | 16 GB | 100 GB | 1 Gbps |
| MongoDB Cluster | 8 vCPU | 32 GB | 1 TB SSD | 10 Gbps |
| Redis Cluster | 4 vCPU | 16 GB | 100 GB | 10 Gbps |
| NATS Cluster | 2 vCPU | 4 GB | 50 GB | 1 Gbps |

### Recommended Production Setup

- **High Availability**: Multi-AZ deployment
- **Auto-scaling**: Based on CPU/memory metrics
- **Backup**: Automated daily backups with 30-day retention
- **Monitoring**: Full observability stack
- **Security**: WAF, DDoS protection, encryption at rest

## Cloud Deployments

### AWS Deployment

#### 1. Infrastructure as Code (Terraform)

```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "ediscovery-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
  enable_dns_hostnames = true
  
  tags = {
    Environment = "production"
    Application = "ediscovery-hypergraph"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "ediscovery-cluster"
  cluster_version = "1.28"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  # Node groups
  eks_managed_node_groups = {
    # General purpose nodes
    general = {
      desired_size = 3
      min_size     = 3
      max_size     = 10
      
      instance_types = ["m5.xlarge"]
      
      k8s_labels = {
        Environment = "production"
        NodeType    = "general"
      }
    }
    
    # AI processing nodes with GPU
    ai = {
      desired_size = 2
      min_size     = 1
      max_size     = 5
      
      instance_types = ["g4dn.xlarge"]
      
      k8s_labels = {
        Environment = "production"
        NodeType    = "ai"
        GPU         = "true"
      }
      
      taints = [{
        key    = "ai-workload"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}

# RDS for PostgreSQL (metadata)
resource "aws_db_instance" "postgres" {
  identifier = "ediscovery-metadata"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  storage_type          = "gp3"
  
  db_name  = "ediscovery"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection = true
  skip_final_snapshot = false
  
  performance_insights_enabled = true
  monitoring_interval         = 60
  
  tags = {
    Environment = "production"
  }
}

# DocumentDB for MongoDB
resource "aws_docdb_cluster" "mongodb" {
  cluster_identifier = "ediscovery-docdb"
  
  engine         = "docdb"
  engine_version = "5.0"
  
  master_username = var.docdb_username
  master_password = var.docdb_password
  
  backup_retention_period = 30
  preferred_backup_window = "03:00-04:00"
  
  vpc_security_group_ids = [aws_security_group.docdb.id]
  db_subnet_group_name   = aws_docdb_subnet_group.main.name
  
  storage_encrypted = true
  kms_key_id       = aws_kms_key.docdb.arn
  
  enabled_cloudwatch_logs_exports = ["audit", "profiler"]
  
  tags = {
    Environment = "production"
  }
}

resource "aws_docdb_cluster_instance" "instances" {
  count = 3
  
  identifier         = "ediscovery-docdb-${count.index}"
  cluster_identifier = aws_docdb_cluster.mongodb.id
  instance_class     = "db.r6g.xlarge"
}

# ElastiCache for Redis
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "ediscovery-redis"
  description          = "Redis cluster for eDiscovery platform"
  
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.r6g.xlarge"
  parameter_group_name = "default.redis7.cluster.on"
  
  num_node_groups         = 3
  replicas_per_node_group = 2
  
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                = var.redis_auth_token
  
  snapshot_retention_limit = 7
  snapshot_window         = "03:00-05:00"
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  tags = {
    Environment = "production"
  }
}

# S3 for document storage
resource "aws_s3_bucket" "documents" {
  bucket = "ediscovery-documents-${var.environment}"
  
  tags = {
    Environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "ediscovery-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
  
  enable_deletion_protection = true
  enable_http2              = true
  enable_cross_zone_load_balancing = true
  
  tags = {
    Environment = "production"
  }
}

# WAF
resource "aws_wafv2_web_acl" "main" {
  name  = "ediscovery-waf"
  scope = "REGIONAL"
  
  default_action {
    allow {}
  }
  
  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 1
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }
  
  # AWS Managed Rules
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSet"
      sampled_requests_enabled   = true
    }
  }
}
```

#### 2. Kubernetes Deployment

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ediscovery
  labels:
    name: ediscovery
    environment: production

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ediscovery-config
  namespace: ediscovery
data:
  ENVIRONMENT: "production"
  PHX_HOST: "api.ediscovery.com"
  POOL_SIZE: "20"
  
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ediscovery-secrets
  namespace: ediscovery
type: Opaque
stringData:
  SECRET_KEY_BASE: "your-secret-key-base"
  OPENAI_API_KEY: "your-openai-api-key"
  DATABASE_URL: "postgresql://user:pass@postgres/ediscovery"

---
# phoenix-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phoenix
  namespace: ediscovery
spec:
  replicas: 3
  selector:
    matchLabels:
      app: phoenix
  template:
    metadata:
      labels:
        app: phoenix
    spec:
      containers:
      - name: phoenix
        image: your-registry/ediscovery-phoenix:latest
        ports:
        - containerPort: 4000
        env:
        - name: PORT
          value: "4000"
        envFrom:
        - configMapRef:
            name: ediscovery-config
        - secretRef:
            name: ediscovery-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 4000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 4000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir: {}
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - phoenix
            topologyKey: kubernetes.io/hostname

---
# python-ai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-ai
  namespace: ediscovery
spec:
  replicas: 3
  selector:
    matchLabels:
      app: python-ai
  template:
    metadata:
      labels:
        app: python-ai
    spec:
      nodeSelector:
        GPU: "true"
      tolerations:
      - key: "ai-workload"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      containers:
      - name: python-ai
        image: your-registry/ediscovery-python:latest
        ports:
        - containerPort: 8001
        env:
        - name: WORKERS
          value: "4"
        envFrom:
        - configMapRef:
            name: ediscovery-config
        - secretRef:
            name: ediscovery-secrets
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: "1"
          limits:
            memory: "8Gi"
            cpu: "4000m"
            nvidia.com/gpu: "1"

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: phoenix-service
  namespace: ediscovery
spec:
  selector:
    app: phoenix
  ports:
  - protocol: TCP
    port: 4000
    targetPort: 4000
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ediscovery-ingress
  namespace: ediscovery
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.ediscovery.com
    secretName: ediscovery-tls
  rules:
  - host: api.ediscovery.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: phoenix-service
            port:
              number: 4000

---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: phoenix-hpa
  namespace: ediscovery
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: phoenix
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
```

### Google Cloud Platform (GCP)

#### 1. Cloud Run Deployment

```yaml
# cloudbuild.yaml
steps:
  # Build Phoenix image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ediscovery-phoenix:$COMMIT_SHA', '-f', 'Dockerfile.phoenix', '.']
  
  # Build Python AI image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ediscovery-python:$COMMIT_SHA', '-f', 'backend/Dockerfile', './backend']
  
  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ediscovery-phoenix:$COMMIT_SHA']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ediscovery-python:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
    - 'run'
    - 'deploy'
    - 'ediscovery-phoenix'
    - '--image=gcr.io/$PROJECT_ID/ediscovery-phoenix:$COMMIT_SHA'
    - '--region=us-central1'
    - '--platform=managed'
    - '--memory=4Gi'
    - '--cpu=2'
    - '--min-instances=3'
    - '--max-instances=100'
    - '--set-env-vars=ENVIRONMENT=production'
    - '--set-secrets=SECRET_KEY_BASE=phoenix-secret:latest,OPENAI_API_KEY=openai-key:latest'

images:
  - 'gcr.io/$PROJECT_ID/ediscovery-phoenix:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/ediscovery-python:$COMMIT_SHA'
```

#### 2. GKE with Anthos

```bash
#!/bin/bash
# deploy-gke.sh

# Create GKE cluster
gcloud container clusters create ediscovery-cluster \
  --zone us-central1-a \
  --node-pool default-pool \
  --num-nodes 3 \
  --machine-type n2-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-stackdriver-kubernetes \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,CloudRun \
  --workload-pool=${PROJECT_ID}.svc.id.goog

# Create GPU node pool
gcloud container node-pools create gpu-pool \
  --cluster=ediscovery-cluster \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --num-nodes=1 \
  --min-nodes=0 \
  --max-nodes=5 \
  --enable-autoscaling

# Install NVIDIA drivers
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml

# Deploy Anthos Service Mesh
curl https://storage.googleapis.com/csm-artifacts/asm/asmcli_1.15 > asmcli
chmod +x asmcli
./asmcli install \
  --project_id ${PROJECT_ID} \
  --cluster_name ediscovery-cluster \
  --cluster_location us-central1-a \
  --enable_all \
  --ca mesh_ca
```

### Azure Deployment

#### 1. Azure Kubernetes Service (AKS)

```bash
#!/bin/bash
# deploy-aks.sh

# Create resource group
az group create --name ediscovery-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group ediscovery-rg \
  --name ediscovery-aks \
  --node-count 3 \
  --node-vm-size Standard_DS3_v2 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --network-plugin azure \
  --network-policy azure

# Add GPU node pool
az aks nodepool add \
  --resource-group ediscovery-rg \
  --cluster-name ediscovery-aks \
  --name gpupool \
  --node-count 1 \
  --node-vm-size Standard_NC6s_v3 \
  --node-taints ai-workload=true:NoSchedule \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 5

# Install NVIDIA device plugin
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.13.0/nvidia-device-plugin.yml

# Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group ediscovery-rg \
  --name ediscovery-postgres \
  --location eastus \
  --tier GeneralPurpose \
  --sku-name Standard_D4s_v3 \
  --storage-size 128 \
  --version 15 \
  --high-availability ZoneRedundant \
  --backup-retention 30
```

## Security Hardening

### 1. Network Security

```yaml
# network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: phoenix-netpol
  namespace: ediscovery
spec:
  podSelector:
    matchLabels:
      app: phoenix
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 4000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

### 2. Pod Security Standards

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: ediscovery-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
```

### 3. Secrets Management

```yaml
# sealed-secret.yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: ediscovery-secrets
  namespace: ediscovery
spec:
  encryptedData:
    OPENAI_API_KEY: AgCd3X5YZ...
    SECRET_KEY_BASE: AgBX4K2PQ...
    DATABASE_URL: AgDM8N3RT...
```

### 4. RBAC Configuration

```yaml
# rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ediscovery-role
  namespace: ediscovery
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ediscovery-rolebinding
  namespace: ediscovery
subjects:
- kind: ServiceAccount
  name: ediscovery-sa
  namespace: ediscovery
roleRef:
  kind: Role
  name: ediscovery-role
  apiGroup: rbac.authorization.k8s.io
```

## Monitoring and Observability

### 1. Prometheus Stack

```yaml
# prometheus-values.yaml
prometheus:
  prometheusSpec:
    retention: 30d
    resources:
      requests:
        cpu: 1000m
        memory: 2Gi
      limits:
        cpu: 2000m
        memory: 4Gi
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 100Gi
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    ruleSelectorNilUsesHelmValues: false

grafana:
  enabled: true
  adminPassword: ${GRAFANA_PASSWORD}
  persistence:
    enabled: true
    size: 10Gi
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: 'default'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards

alertmanager:
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 10Gi
```

### 2. Application Metrics

```elixir
# Elixir Telemetry Configuration
defmodule EdiscoveryWeb.Telemetry do
  use Supervisor
  import Telemetry.Metrics

  def start_link(arg) do
    Supervisor.start_link(__MODULE__, arg, name: __MODULE__)
  end

  def init(_arg) do
    children = [
      {TelemetryMetricsPrometheus, metrics: metrics()}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end

  def metrics do
    [
      # Phoenix Metrics
      summary("phoenix.endpoint.stop.duration",
        unit: {:native, :millisecond},
        tags: [:method, :route, :status]
      ),
      
      # Database Metrics
      summary("ediscovery.repo.query.total_time",
        unit: {:native, :millisecond},
        tags: [:source, :command]
      ),
      
      # Business Metrics
      counter("ediscovery.document.processed",
        tags: [:case_id, :status]
      ),
      
      counter("ediscovery.workflow.completed",
        tags: [:workflow_type, :status]
      ),
      
      summary("ediscovery.ai.processing_time",
        unit: {:native, :millisecond},
        tags: [:operation, :model]
      ),
      
      # System Metrics
      last_value("vm.memory.total", unit: :byte),
      last_value("vm.total_run_queue_lengths.total"),
      last_value("vm.total_run_queue_lengths.cpu"),
      summary("vm.total_run_queue_lengths.io")
    ]
  end
end
```

### 3. Distributed Tracing

```yaml
# jaeger-values.yaml
jaeger:
  create: true
  spec:
    strategy: production
    storage:
      type: elasticsearch
      options:
        es:
          server-urls: http://elasticsearch:9200
          index-prefix: jaeger
    ingress:
      enabled: true
      hosts:
        - jaeger.ediscovery.com
    collector:
      maxReplicas: 5
      resources:
        limits:
          cpu: 1
          memory: 1Gi
    query:
      resources:
        limits:
          cpu: 500m
          memory: 512Mi
```

## Backup and Disaster Recovery

### 1. Automated Backups

```bash
#!/bin/bash
# backup.sh

# MongoDB backup
mongodump \
  --uri="${MONGODB_URI}" \
  --archive="/backup/mongodb-$(date +%Y%m%d-%H%M%S).archive" \
  --gzip

# PostgreSQL backup
pg_dump "${DATABASE_URL}" | gzip > "/backup/postgres-$(date +%Y%m%d-%H%M%S).sql.gz"

# S3 sync
aws s3 sync /backup s3://${BACKUP_BUCKET}/backups/$(date +%Y/%m/%d)/ \
  --storage-class GLACIER

# Kubernetes resources backup
velero backup create ediscovery-backup-$(date +%Y%m%d) \
  --include-namespaces ediscovery \
  --ttl 720h
```

### 2. Disaster Recovery Plan

```yaml
# disaster-recovery.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dr-procedures
  namespace: ediscovery
data:
  rto: "4 hours"  # Recovery Time Objective
  rpo: "1 hour"   # Recovery Point Objective
  
  procedures: |
    1. Database Recovery:
       - Restore MongoDB from latest snapshot
       - Restore PostgreSQL from latest backup
       - Verify data integrity
    
    2. Application Recovery:
       - Deploy to DR region using terraform
       - Update DNS to point to DR region
       - Verify all services are healthy
    
    3. Data Verification:
       - Run integrity checks
       - Verify document counts
       - Test critical workflows
```

## Performance Tuning

### 1. Application Optimization

```elixir
# config/prod.exs
config :a2a_agent_web, A2AAgentWeb.Endpoint,
  http: [
    port: 4000,
    transport_options: [
      num_acceptors: 100,
      max_connections: 16_384
    ]
  ]

config :a2a_agent_web, A2AAgentWeb.Repo,
  pool_size: 50,
  queue_target: 5000,
  queue_interval: 1000,
  migration_lock: false

config :phoenix, :json_library, Jason
config :jason, :decode_option, strings: :copy
```

### 2. Database Optimization

```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET random_page_cost = 1.1;

-- Create indexes
CREATE INDEX CONCURRENTLY idx_documents_case_id_status 
ON documents(case_id, status) 
WHERE status != 'deleted';

CREATE INDEX CONCURRENTLY idx_documents_processed_at 
ON documents(processed_at DESC) 
WHERE processed_at IS NOT NULL;

-- Partitioning for large tables
CREATE TABLE documents_2024 PARTITION OF documents
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 3. Caching Strategy

```elixir
defmodule EdiscoveryWeb.CacheStrategy do
  @moduledoc """
  Multi-layer caching strategy
  """
  
  # L1: Process cache (ETS)
  def get_l1(key) do
    case :ets.lookup(:l1_cache, key) do
      [{^key, value, expiry}] when expiry > System.os_time(:second) ->
        {:ok, value}
      _ ->
        :miss
    end
  end
  
  # L2: Redis cache
  def get_l2(key) do
    case Redix.command(:redix, ["GET", key]) do
      {:ok, nil} -> :miss
      {:ok, value} -> {:ok, :erlang.binary_to_term(value)}
      _ -> :miss
    end
  end
  
  # L3: Database
  def get_l3(key) do
    # Database query
  end
  
  def get(key) do
    with :miss <- get_l1(key),
         :miss <- get_l2(key),
         :miss <- get_l3(key) do
      nil
    else
      {:ok, value} = result ->
        warm_upper_caches(key, value)
        result
    end
  end
end
```

## Compliance and Auditing

### 1. Audit Logging

```yaml
# fluent-bit-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: ediscovery
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Daemon       Off
        Log_Level    info
        
    [INPUT]
        Name              tail
        Path              /var/log/containers/*ediscovery*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5
        
    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        
    [OUTPUT]
        Name   s3
        Match  *
        bucket audit-logs
        region us-east-1
        use_put_object On
        total_file_size 50M
        upload_timeout 10m
```

### 2. Compliance Monitoring

```python
# compliance_monitor.py
import asyncio
from datetime import datetime, timedelta

class ComplianceMonitor:
    def __init__(self):
        self.checks = [
            self.check_data_retention,
            self.check_access_controls,
            self.check_encryption,
            self.check_audit_integrity,
            self.check_gdpr_compliance
        ]
    
    async def run_compliance_checks(self):
        results = []
        for check in self.checks:
            try:
                result = await check()
                results.append(result)
            except Exception as e:
                results.append({
                    "check": check.__name__,
                    "status": "error",
                    "message": str(e)
                })
        
        report = self.generate_compliance_report(results)
        await self.notify_compliance_team(report)
        
        return report
    
    async def check_data_retention(self):
        # Check documents past retention period
        expired_docs = await self.db.documents.find({
            "retention_date": {"$lt": datetime.utcnow()},
            "status": {"$ne": "deleted"}
        })
        
        if expired_docs:
            return {
                "check": "data_retention",
                "status": "warning",
                "count": len(expired_docs),
                "action": "schedule_deletion"
            }
        
        return {"check": "data_retention", "status": "passed"}
```

## Maintenance and Updates

### 1. Blue-Green Deployment

```bash
#!/bin/bash
# blue-green-deploy.sh

# Deploy to green environment
kubectl apply -f k8s/green/

# Run smoke tests
./scripts/smoke-tests.sh green

if [ $? -eq 0 ]; then
    # Switch traffic to green
    kubectl patch service ediscovery-service -p \
      '{"spec":{"selector":{"version":"green"}}}'
    
    # Monitor for 5 minutes
    sleep 300
    
    # If stable, remove blue
    kubectl delete -f k8s/blue/
else
    echo "Smoke tests failed, rolling back"
    kubectl delete -f k8s/green/
fi
```

### 2. Canary Deployment

```yaml
# flagger-canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: ediscovery-phoenix
  namespace: ediscovery
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: phoenix
  service:
    port: 4000
  analysis:
    interval: 1m
    threshold: 10
    maxWeight: 50
    stepWeight: 5
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: smoke-tests
      url: http://flagger-loadtester.test/
      timeout: 5m
      metadata:
        type: smoke
        cmd: "./scripts/canary-tests.sh"
```

## Next Steps

- Review [Docker Deployment](/deployment/docker) for containerization
- Check [Examples](/examples) for production configurations
- See [Support](/support) for troubleshooting help