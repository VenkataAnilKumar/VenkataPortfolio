# Security Architecture

## Security Overview

The Codebase Intelligence Engine implements a comprehensive security model based on defense-in-depth principles, zero-trust architecture, and industry best practices. Security is embedded at every layer from network to application to data.

## Security Principles

1. **Zero Trust**: Never trust, always verify
2. **Least Privilege**: Minimal access rights for users and services
3. **Defense in Depth**: Multiple layers of security controls
4. **Secure by Default**: Security controls enabled by default
5. **Privacy by Design**: Data protection built into the system
6. **Transparency**: Security actions are logged and auditable

## Identity and Access Management (IAM)

### Authentication Architecture

#### Multi-Factor Authentication (MFA)
```yaml
# MFA configuration
authentication:
  providers:
    - name: github_oauth
      type: oauth2
      config:
        client_id: ${GITHUB_CLIENT_ID}
        client_secret: ${GITHUB_CLIENT_SECRET}
        scopes: [user:email, read:org]
        mfa_required: true
    
    - name: saml_sso
      type: saml
      config:
        entity_id: "codebase-intelligence"
        sso_url: "${SAML_SSO_URL}"
        certificate: "${SAML_CERTIFICATE}"
        mfa_required: true
    
    - name: api_key
      type: api_key
      config:
        header_name: "X-API-Key"
        rate_limit: 10000  # per hour
        require_ip_whitelist: true

  session:
    timeout: 3600  # 1 hour
    refresh_threshold: 300  # 5 minutes
    secure_cookie: true
    same_site: strict
```

#### JWT Token Management
```json
{
  "jwt_config": {
    "issuer": "https://auth.codebase-intelligence.com",
    "audience": "https://api.codebase-intelligence.com",
    "signing_algorithm": "ES256",
    "key_rotation_interval": "24h",
    "token_lifetime": "1h",
    "refresh_token_lifetime": "30d",
    "claims": {
      "user_id": "string",
      "organization_id": "string",
      "roles": ["array"],
      "permissions": ["array"],
      "mfa_verified": "boolean",
      "ip_address": "string"
    }
  }
}
```

### Authorization Framework

#### Role-Based Access Control (RBAC)
```yaml
# RBAC definitions
roles:
  - name: "organization_owner"
    permissions:
      - "org:*"
      - "repo:*"
      - "user:*"
      - "billing:*"
    
  - name: "organization_admin"
    permissions:
      - "org:read"
      - "org:write"
      - "repo:*"
      - "user:read"
      - "user:invite"
    
  - name: "developer"
    permissions:
      - "repo:read"
      - "repo:scan"
      - "findings:read"
      - "findings:update"
      - "plans:read"
      - "plans:create"
    
  - name: "viewer"
    permissions:
      - "repo:read"
      - "findings:read"
      - "plans:read"

# Permission hierarchy
permission_groups:
  - name: "repository_permissions"
    permissions:
      - "repo:read"
      - "repo:write"
      - "repo:admin"
      - "repo:scan"
      - "repo:delete"
  
  - name: "finding_permissions"
    permissions:
      - "findings:read"
      - "findings:update"
      - "findings:resolve"
      - "findings:dismiss"
```

#### Attribute-Based Access Control (ABAC)
```json
{
  "policy_engine": {
    "rules": [
      {
        "id": "repository_access_rule",
        "description": "Users can only access repositories in their organization",
        "condition": "user.organization_id == resource.repository.organization_id",
        "effect": "ALLOW"
      },
      {
        "id": "sensitive_repository_rule",
        "description": "Sensitive repositories require additional approval",
        "condition": "resource.repository.sensitivity == 'high' AND user.clearance_level >= 'secret'",
        "effect": "ALLOW"
      },
      {
        "id": "time_based_access_rule",
        "description": "Restrict access during maintenance windows",
        "condition": "NOT (time.hour >= 2 AND time.hour <= 4)",
        "effect": "ALLOW"
      }
    ]
  }
}
```

## Network Security

### Network Segmentation
```yaml
# Network security policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: codebase-intelligence-network-policy
  namespace: codebase-intelligence
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 3000
  
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
```

### TLS/SSL Configuration
```yaml
# TLS certificate management
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: codebase-intelligence-tls
  namespace: codebase-intelligence
spec:
  secretName: codebase-intelligence-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - api.codebase-intelligence.com
  - app.codebase-intelligence.com
  - "*.codebase-intelligence.com"

---
# TLS policy enforcement
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: tls-policy
spec:
  host: "*.codebase-intelligence.svc.cluster.local"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
      minProtocolVersion: TLSV1_3
      cipherSuites:
      - ECDHE-ECDSA-AES256-GCM-SHA384
      - ECDHE-RSA-AES256-GCM-SHA384
```

## Data Security

### Encryption Strategy

#### Encryption at Rest
```yaml
# Database encryption
postgresql_config:
  encryption:
    method: "AES-256-GCM"
    key_management: "AWS KMS"
    key_rotation: "90d"
    column_encryption:
      - table: "users"
        columns: ["email", "provider_id"]
      - table: "repositories"
        columns: ["clone_url", "credentials"]

neo4j_config:
  encryption:
    enabled: true
    cipher: "AES-256-CBC"
    key_derivation: "PBKDF2"

# Object storage encryption
s3_encryption:
  default_encryption:
    sse_algorithm: "aws:kms"
    kms_master_key_id: "arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789012"
  bucket_key_enabled: true
```

#### Encryption in Transit
```yaml
# Service-to-service encryption
istio_config:
  mtls:
    mode: STRICT
    cipher_suites:
    - ECDHE-ECDSA-AES256-GCM-SHA384
    - ECDHE-RSA-AES256-GCM-SHA384
    min_protocol_version: TLSv1_3
    
# External API encryption
nginx_config:
  ssl_protocols: "TLSv1.3"
  ssl_ciphers: "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
  ssl_prefer_server_ciphers: on
  ssl_session_cache: "shared:SSL:10m"
  ssl_session_timeout: "10m"
```

### Data Classification and Handling

#### Data Classification Schema
```yaml
# Data classification levels
data_classification:
  levels:
    - name: "public"
      description: "Information that can be freely shared"
      retention: "unlimited"
      encryption_required: false
      
    - name: "internal"
      description: "Information for internal use only"
      retention: "7_years"
      encryption_required: true
      
    - name: "confidential"
      description: "Sensitive business information"
      retention: "5_years"
      encryption_required: true
      access_logging: true
      
    - name: "restricted"
      description: "Highly sensitive information"
      retention: "3_years"
      encryption_required: true
      access_logging: true
      approval_required: true

# Automatic data classification rules
classification_rules:
  - pattern: ".*password.*|.*secret.*|.*key.*"
    classification: "restricted"
    action: "redact"
    
  - pattern: ".*email.*|.*phone.*|.*ssn.*"
    classification: "confidential"
    action: "encrypt"
    
  - pattern: ".*\.git/.*|.*node_modules/.*"
    classification: "internal"
    action: "exclude"
```

#### Data Loss Prevention (DLP)
```yaml
# DLP policies
dlp_policies:
  - name: "prevent_secret_exposure"
    description: "Prevent API keys and secrets from being exposed"
    rules:
      - pattern: "(?i)(api[_-]?key|secret|token|password)\\s*[:=]\\s*['\"]([^'\"\\s]+)['\"]"
        action: "block"
        severity: "high"
        
  - name: "pii_detection"
    description: "Detect and protect personally identifiable information"
    rules:
      - pattern: "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN
        action: "redact"
        replacement: "XXX-XX-XXXX"
        
      - pattern: "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"  # Email
        action: "redact"
        replacement: "[EMAIL_REDACTED]"
```

## Application Security

### Secure Development Lifecycle (SDL)

#### Security Code Review
```yaml
# Automated security scanning
security_scanning:
  static_analysis:
    tools:
      - name: "semgrep"
        config: "p/security-audit"
        fail_on: "error"
        
      - name: "bandit"
        config: "high_severity"
        languages: ["python"]
        
      - name: "gosec"
        languages: ["go"]
        
  dependency_scanning:
    tools:
      - name: "snyk"
        fail_on: "high"
        
      - name: "npm_audit"
        languages: ["javascript"]
        
  container_scanning:
    tools:
      - name: "trivy"
        fail_on: "critical"
        
      - name: "clair"
        registry_integration: true
```

#### Runtime Application Self-Protection (RASP)
```yaml
# RASP configuration
rasp_config:
  monitors:
    - type: "sql_injection"
      action: "block"
      sensitivity: "high"
      
    - type: "command_injection"
      action: "block"
      sensitivity: "high"
      
    - type: "path_traversal"
      action: "block"
      sensitivity: "medium"
      
    - type: "xss"
      action: "sanitize"
      sensitivity: "medium"
      
  reporting:
    endpoint: "https://security-events.codebase-intelligence.com"
    format: "json"
    real_time: true
```

### Input Validation and Sanitization

#### API Input Validation
```javascript
// Input validation schemas
const validationSchemas = {
  repositoryCreate: {
    type: 'object',
    required: ['name', 'url', 'provider'],
    properties: {
      name: {
        type: 'string',
        pattern: '^[a-zA-Z0-9_-]+$',
        maxLength: 255,
        minLength: 1
      },
      url: {
        type: 'string',
        format: 'uri',
        pattern: '^https?://'
      },
      provider: {
        type: 'string',
        enum: ['github', 'gitlab', 'azure', 'bitbucket']
      }
    },
    additionalProperties: false
  },
  
  findingUpdate: {
    type: 'object',
    required: ['status'],
    properties: {
      status: {
        type: 'string',
        enum: ['acknowledged', 'resolved', 'false_positive']
      },
      comment: {
        type: 'string',
        maxLength: 1000,
        pattern: '^[\\w\\s.,!?-]*$'  // Alphanumeric, spaces, basic punctuation
      }
    },
    additionalProperties: false
  }
};

// SQL injection prevention
const sanitizeSQLInput = (input) => {
  // Use parameterized queries exclusively
  const query = 'SELECT * FROM repositories WHERE organization_id = $1 AND status = $2';
  return db.query(query, [organizationId, status]);
};

// XSS prevention
const sanitizeHTMLOutput = (content) => {
  return DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre'],
    ALLOWED_ATTR: []
  });
};
```

## Infrastructure Security

### Container Security

#### Container Image Security
```dockerfile
# Multi-stage build for minimal attack surface
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runtime
# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Install security updates
RUN apk update && apk upgrade && \
    apk add --no-cache dumb-init && \
    rm -rf /var/cache/apk/*

WORKDIR /app
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .

# Remove unnecessary files
RUN rm -rf /app/test /app/docs /app/.git

# Set security headers
USER nodejs
EXPOSE 3000

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

#### Runtime Security
```yaml
# Pod Security Standards
apiVersion: v1
kind: Pod
metadata:
  name: codebase-intelligence-service
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    runAsGroup: 1001
    fsGroup: 1001
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: app
    image: codebase-intelligence/service:v1.0.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE  # Only if needed for port 80/443
    
    resources:
      limits:
        cpu: 1000m
        memory: 2Gi
        ephemeral-storage: 1Gi
      requests:
        cpu: 500m
        memory: 1Gi
        ephemeral-storage: 500Mi
    
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /app/cache
  
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
```

### Secrets Management

#### HashiCorp Vault Integration
```yaml
# Vault configuration
vault_config:
  auth_methods:
    - name: "kubernetes"
      type: "kubernetes"
      config:
        kubernetes_host: "https://kubernetes.default.svc.cluster.local"
        kubernetes_ca_cert: "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
        token_reviewer_jwt_file: "/var/run/secrets/kubernetes.io/serviceaccount/token"
  
  secret_engines:
    - name: "database"
      type: "database"
      config:
        plugin_name: "postgresql-database-plugin"
        connection_url: "postgresql://{{username}}:{{password}}@postgres:5432/codebase_intelligence"
        max_open_connections: 5
        max_idle_connections: 0
        max_connection_lifetime: "5m"
        
    - name: "github"
      type: "kv-v2"
      description: "GitHub integration secrets"
      
  policies:
    - name: "codebase-intelligence-read"
      rules: |
        path "database/creds/readonly" {
          capabilities = ["read"]
        }
        path "github/data/oauth" {
          capabilities = ["read"]
        }
```

#### Kubernetes Secrets
```yaml
# External Secrets Operator configuration
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-secret-store
spec:
  provider:
    vault:
      server: "https://vault.codebase-intelligence.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "codebase-intelligence"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-secret-store
    kind: SecretStore
  target:
    name: database-credentials
    creationPolicy: Owner
  data:
  - secretKey: url
    remoteRef:
      key: database
      property: connection_url
  - secretKey: username
    remoteRef:
      key: database
      property: username
  - secretKey: password
    remoteRef:
      key: database
      property: password
```

## Security Monitoring and Incident Response

### Security Information and Event Management (SIEM)

#### Security Event Collection
```yaml
# Security event schema
security_event:
  timestamp: "2025-01-15T10:30:00Z"
  event_id: "uuid"
  event_type: "authentication|authorization|data_access|security_violation"
  severity: "low|medium|high|critical"
  source: "service_name"
  user_id: "uuid"
  session_id: "uuid"
  ip_address: "x.x.x.x"
  user_agent: "string"
  resource: "api_endpoint|database_table|file_path"
  action: "read|write|delete|execute"
  result: "success|failure|blocked"
  details: {
    "request_id": "uuid",
    "method": "GET|POST|PUT|DELETE",
    "url": "string",
    "response_code": "integer",
    "response_time": "integer",
    "risk_score": "float"
  }
```

#### Automated Threat Detection
```yaml
# Security rules
security_rules:
  - name: "brute_force_detection"
    description: "Detect brute force authentication attempts"
    condition: "count(failed_login) > 5 in 5 minutes from same IP"
    action: "block_ip"
    severity: "high"
    
  - name: "privilege_escalation"
    description: "Detect attempts to access higher privilege resources"
    condition: "user.role != 'admin' AND accessed_resource.requires_admin = true"
    action: "alert"
    severity: "critical"
    
  - name: "anomalous_data_access"
    description: "Detect unusual data access patterns"
    condition: "data_access_volume > user.baseline * 10"
    action: "alert"
    severity: "medium"
    
  - name: "suspicious_api_usage"
    description: "Detect potential API abuse"
    condition: "api_requests > rate_limit * 0.9 in 1 minute"
    action: "throttle"
    severity: "low"
```

### Incident Response

#### Automated Response Playbooks
```yaml
# Incident response automation
incident_response:
  triggers:
    - event_type: "security_violation"
      severity: "critical"
      actions:
        - "create_incident"
        - "notify_security_team"
        - "block_source_ip"
        - "revoke_user_sessions"
        
    - event_type: "data_breach_suspected"
      actions:
        - "create_incident"
        - "notify_legal_team"
        - "enable_enhanced_logging"
        - "freeze_data_exports"
        
  escalation_matrix:
    - severity: "low"
      notification: "email"
      response_time: "4_hours"
      
    - severity: "medium"
      notification: "email_and_slack"
      response_time: "1_hour"
      
    - severity: "high"
      notification: "email_slack_and_phone"
      response_time: "15_minutes"
      
    - severity: "critical"
      notification: "all_channels"
      response_time: "immediate"
```

## Compliance and Governance

### Regulatory Compliance

#### SOC 2 Controls
```yaml
# SOC 2 Type II controls mapping
soc2_controls:
  security:
    - control_id: "CC6.1"
      description: "Logical and physical access controls"
      implementation:
        - "Multi-factor authentication"
        - "Role-based access control"
        - "Network segmentation"
        - "Physical datacenter security"
      evidence:
        - "Access logs"
        - "User provisioning records"
        - "Network configuration"
        
  availability:
    - control_id: "CC7.1"
      description: "System availability monitoring"
      implementation:
        - "Health checks and monitoring"
        - "Automated failover"
        - "Backup and recovery procedures"
      evidence:
        - "Uptime metrics"
        - "Incident reports"
        - "Recovery test results"
```

#### GDPR Compliance
```yaml
# GDPR data protection measures
gdpr_compliance:
  data_minimization:
    - "Collect only necessary data"
    - "Regular data audits and cleanup"
    - "Automated data retention policies"
    
  consent_management:
    - "Explicit consent for data processing"
    - "Granular consent options"
    - "Easy consent withdrawal"
    
  data_subject_rights:
    - "Right to access (data export)"
    - "Right to rectification (data correction)"
    - "Right to erasure (data deletion)"
    - "Right to portability (data transfer)"
    
  privacy_by_design:
    - "Data protection impact assessments"
    - "Privacy-preserving architectures"
    - "Regular privacy audits"
```

### Security Auditing

#### Continuous Security Assessment
```yaml
# Security assessment schedule
security_assessments:
  vulnerability_scanning:
    frequency: "weekly"
    tools: ["nessus", "openvas", "trivy"]
    scope: "all_systems"
    
  penetration_testing:
    frequency: "quarterly"
    scope: "external_and_internal"
    methodology: "owasp_testing_guide"
    
  code_security_review:
    frequency: "per_release"
    tools: ["semgrep", "sonarqube", "veracode"]
    coverage: "100%"
    
  security_architecture_review:
    frequency: "annually"
    scope: "entire_system"
    framework: "nist_cybersecurity_framework"
```

This comprehensive security architecture ensures that the Codebase Intelligence Engine maintains the highest levels of security, privacy, and compliance while enabling secure access to sensitive code analysis capabilities.