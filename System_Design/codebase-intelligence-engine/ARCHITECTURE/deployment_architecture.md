# Deployment Architecture

## Overview

The Codebase Intelligence Engine is designed for cloud-native deployment with support for multiple cloud providers and on-premises installations. The architecture emphasizes high availability, scalability, security, and operational excellence.

## Cloud-Native Architecture

### Container Strategy
```yaml
# Base container specifications
containers:
  api-gateway:
    image: nginx:alpine
    resources:
      cpu: 500m
      memory: 512Mi
    replicas: 3
    
  ingestion-service:
    image: node:18-alpine
    resources:
      cpu: 1000m
      memory: 2Gi
    replicas: 5
    
  parser-service:
    image: python:3.11-slim
    resources:
      cpu: 2000m
      memory: 4Gi
    replicas: 10
    
  graph-service:
    image: node:18-alpine
    resources:
      cpu: 1500m
      memory: 3Gi
    replicas: 3
    
  ai-analysis-engine:
    image: python:3.11-gpu
    resources:
      gpu: 1
      cpu: 4000m
      memory: 8Gi
    replicas: 2
    
  refactoring-planner:
    image: python:3.11-slim
    resources:
      cpu: 1500m
      memory: 3Gi
    replicas: 3
    
  safety-engine:
    image: node:18-alpine
    resources:
      cpu: 1000m
      memory: 2Gi
    replicas: 2
```

## Kubernetes Deployment

### Namespace Organization
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: codebase-intelligence
  labels:
    app.kubernetes.io/name: codebase-intelligence
    app.kubernetes.io/version: "1.0.0"
---
apiVersion: v1
kind: Namespace
metadata:
  name: codebase-intelligence-monitoring
  labels:
    app.kubernetes.io/name: monitoring
```

### Core Services Deployment
```yaml
# API Gateway Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: codebase-intelligence
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        - containerPort: 443
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
        - name: ssl-certs
          mountPath: /etc/ssl/certs
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
      - name: ssl-certs
        secret:
          secretName: ssl-certificates

---
# Ingestion Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingestion-service
  namespace: codebase-intelligence
spec:
  replicas: 5
  selector:
    matchLabels:
      app: ingestion-service
  template:
    metadata:
      labels:
        app: ingestion-service
    spec:
      containers:
      - name: ingestion
        image: codebase-intelligence/ingestion:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        - name: MESSAGE_QUEUE_URL
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: url
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
```

### Database Deployments
```yaml
# PostgreSQL StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: codebase-intelligence
spec:
  serviceName: postgresql-headless
  replicas: 3
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: codebase_intelligence
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgresql-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgresql-credentials
              key: password
        - name: POSTGRES_REPLICATION_MODE
          value: slave
        - name: POSTGRES_MASTER_SERVICE
          value: postgresql
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgresql-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
  volumeClaimTemplates:
  - metadata:
      name: postgresql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
      storageClassName: fast-ssd

---
# Neo4j StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: neo4j
  namespace: codebase-intelligence
spec:
  serviceName: neo4j-headless
  replicas: 3
  selector:
    matchLabels:
      app: neo4j
  template:
    metadata:
      labels:
        app: neo4j
    spec:
      containers:
      - name: neo4j
        image: neo4j:5.13-enterprise
        env:
        - name: NEO4J_AUTH
          valueFrom:
            secretKeyRef:
              name: neo4j-credentials
              key: auth
        - name: NEO4J_ACCEPT_LICENSE_AGREEMENT
          value: "yes"
        - name: NEO4J_dbms_mode
          value: CORE
        - name: NEO4J_causal__clustering_initial__discovery__members
          value: "neo4j-0.neo4j-headless:5000,neo4j-1.neo4j-headless:5000,neo4j-2.neo4j-headless:5000"
        ports:
        - containerPort: 7474
        - containerPort: 7687
        - containerPort: 5000
        - containerPort: 6000
        volumeMounts:
        - name: neo4j-data
          mountPath: /data
        - name: neo4j-logs
          mountPath: /logs
        resources:
          requests:
            cpu: 2000m
            memory: 4Gi
          limits:
            cpu: 4000m
            memory: 8Gi
  volumeClaimTemplates:
  - metadata:
      name: neo4j-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 200Gi
      storageClassName: fast-ssd
  - metadata:
      name: neo4j-logs
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

### Service Mesh Configuration (Istio)
```yaml
# Virtual Service for traffic routing
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: codebase-intelligence-vs
  namespace: codebase-intelligence
spec:
  hosts:
  - api.codebase-intelligence.com
  gateways:
  - codebase-intelligence-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1/repositories
    route:
    - destination:
        host: ingestion-service
        port:
          number: 3000
    retries:
      attempts: 3
      perTryTimeout: 30s
    timeout: 90s
  - match:
    - uri:
        prefix: /api/v1/graph
    route:
    - destination:
        host: graph-service
        port:
          number: 3000
    retries:
      attempts: 3
      perTryTimeout: 10s
  - match:
    - uri:
        prefix: /api/v1/analyze
    route:
    - destination:
        host: ai-analysis-engine
        port:
          number: 5000
    timeout: 300s

---
# Destination Rule for load balancing
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: codebase-intelligence-dr
  namespace: codebase-intelligence
spec:
  host: "*.codebase-intelligence.svc.cluster.local"
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 10
    circuitBreaker:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

## High Availability Setup

### Multi-Region Deployment
```yaml
# Global load balancer configuration
apiVersion: v1
kind: Service
metadata:
  name: global-load-balancer
  annotations:
    networking.gke.io/load-balancer-type: "External"
    cloud.google.com/global-access: "true"
spec:
  type: LoadBalancer
  selector:
    app: api-gateway
  ports:
  - port: 443
    targetPort: 443
    protocol: TCP
  loadBalancerSourceRanges:
  - 0.0.0.0/0

---
# Cross-region database replication
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgresql-cluster
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
  bootstrap:
    initdb:
      database: codebase_intelligence
      owner: app_user
  storage:
    size: 100Gi
    storageClass: fast-ssd
  monitoring:
    enabled: true
  backup:
    retentionPolicy: "30d"
    barmanObjectStore:
      destinationPath: "s3://codebase-intelligence-backups"
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: access-key-id
        secretAccessKey:
          name: backup-credentials
          key: secret-access-key
```

### Auto-scaling Configuration
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ingestion-service-hpa
  namespace: codebase-intelligence
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ingestion-service
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
  - type: Pods
    pods:
      metric:
        name: queue_depth
      target:
        type: AverageValue
        averageValue: "10"

---
# Vertical Pod Autoscaler
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: ai-analysis-engine-vpa
  namespace: codebase-intelligence
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-analysis-engine
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: ai-analysis
      maxAllowed:
        cpu: 8000m
        memory: 16Gi
      minAllowed:
        cpu: 1000m
        memory: 2Gi
```

## Infrastructure as Code (Terraform)

### AWS Infrastructure
```hcl
# terraform/aws/main.tf
provider "aws" {
  region = var.aws_region
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "codebase-intelligence-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway   = true
  enable_vpn_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Terraform = "true"
    Environment = var.environment
    Project = "codebase-intelligence"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "codebase-intelligence-${var.environment}"
  cluster_version = "1.28"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  # Node groups
  node_groups = {
    general = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 1
      
      instance_types = ["t3.large"]
      
      k8s_labels = {
        Environment = var.environment
        NodeGroup   = "general"
      }
    }
    
    compute_intensive = {
      desired_capacity = 2
      max_capacity     = 5
      min_capacity     = 0
      
      instance_types = ["c5.2xlarge"]
      
      k8s_labels = {
        Environment = var.environment
        NodeGroup   = "compute-intensive"
      }
      
      taints = [{
        key    = "compute-intensive"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
    
    gpu_nodes = {
      desired_capacity = 1
      max_capacity     = 3
      min_capacity     = 0
      
      instance_types = ["p3.2xlarge"]
      
      k8s_labels = {
        Environment = var.environment
        NodeGroup   = "gpu"
      }
      
      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgresql" {
  identifier = "codebase-intelligence-${var.environment}"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r5.xlarge"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  
  db_name  = "codebase_intelligence"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "production"
  
  tags = {
    Name        = "codebase-intelligence-${var.environment}"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "codebase-intelligence-${var.environment}"
  description                = "Redis cluster for codebase intelligence"
  
  node_type          = "cache.r5.large"
  num_cache_clusters = 3
  
  engine_version     = "7.0"
  parameter_group_name = "default.redis7"
  port               = 6379
  
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name        = "codebase-intelligence-${var.environment}"
    Environment = var.environment
  }
}

# S3 Buckets
resource "aws_s3_bucket" "artifacts" {
  bucket = "codebase-intelligence-artifacts-${var.environment}-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name        = "artifacts-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.s3.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}
```

### Google Cloud Infrastructure
```hcl
# terraform/gcp/main.tf
provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "codebase-intelligence-${var.environment}"
  location = var.region
  
  remove_default_node_pool = true
  initial_node_count       = 1
  
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
  
  # Enable workload identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  # Enable network policy
  network_policy {
    enabled = true
  }
  
  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  
  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "10.0.0.0/16"
      display_name = "VPC"
    }
  }
}

# Node pools
resource "google_container_node_pool" "general_nodes" {
  name       = "general-pool"
  cluster    = google_container_cluster.primary.name
  location   = var.region
  node_count = 3
  
  autoscaling {
    min_node_count = 1
    max_node_count = 10
  }
  
  node_config {
    preemptible  = false
    machine_type = "e2-standard-4"
    
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    labels = {
      environment = var.environment
      node-pool   = "general"
    }
    
    tags = ["gke-node", "codebase-intelligence"]
  }
}

resource "google_container_node_pool" "gpu_nodes" {
  name       = "gpu-pool"
  cluster    = google_container_cluster.primary.name
  location   = var.region
  node_count = 0
  
  autoscaling {
    min_node_count = 0
    max_node_count = 3
  }
  
  node_config {
    preemptible  = true
    machine_type = "n1-standard-4"
    
    guest_accelerator {
      type  = "nvidia-tesla-t4"
      count = 1
    }
    
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    labels = {
      environment = var.environment
      node-pool   = "gpu"
    }
    
    taint {
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
  }
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "main" {
  name             = "codebase-intelligence-${var.environment}"
  database_version = "POSTGRES_15"
  region          = var.region
  
  settings {
    tier = "db-custom-4-16384"
    
    disk_type    = "PD_SSD"
    disk_size    = 100
    disk_autoresize = true
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
    
    database_flags {
      name  = "max_connections"
      value = "200"
    }
  }
  
  deletion_protection = var.environment == "production"
}
```

## Monitoring and Observability

### Prometheus Configuration
```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
    - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: default;kubernetes;https

  - job_name: 'codebase-intelligence-services'
    kubernetes_sd_configs:
    - role: endpoints
      namespaces:
        names:
        - codebase-intelligence
    relabel_configs:
    - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "Codebase Intelligence Engine",
    "panels": [
      {
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Scan Queue Depth",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rabbitmq_queue_messages{queue=\"parsing\"}",
            "legendFormat": "Parsing Queue"
          }
        ]
      },
      {
        "title": "Database Connection Pool",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_activity_count",
            "legendFormat": "Active Connections"
          }
        ]
      }
    ]
  }
}
```

## Disaster Recovery

### Backup Strategy
```yaml
# Velero backup configuration
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: codebase-intelligence-daily
  namespace: velero
spec:
  includedNamespaces:
  - codebase-intelligence
  storageLocation: default
  volumeSnapshotLocations:
  - default
  ttl: 720h0m0s
  schedule: "0 2 * * *"

---
# Database backup CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgresql-backup
  namespace: codebase-intelligence
spec:
  schedule: "0 1 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/bash
            - -c
            - |
              pg_dump $DATABASE_URL | gzip | aws s3 cp - s3://codebase-intelligence-backups/postgresql/$(date +%Y%m%d_%H%M%S).sql.gz
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-credentials
                  key: url
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: backup-credentials
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: backup-credentials
                  key: secret-access-key
          restartPolicy: OnFailure
```

This comprehensive deployment architecture provides a robust, scalable, and secure foundation for the Codebase Intelligence Engine with support for multiple cloud providers, high availability, auto-scaling, monitoring, and disaster recovery.