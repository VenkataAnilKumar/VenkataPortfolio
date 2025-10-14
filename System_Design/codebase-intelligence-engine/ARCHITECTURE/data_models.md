# Data Models and Database Schemas

## Database Architecture Overview

The Codebase Intelligence Engine uses a polyglot persistence approach with different storage systems optimized for specific data types:

- **PostgreSQL**: Relational data (repositories, users, configurations, metadata)
- **Neo4j**: Graph data (code relationships, dependencies, call graphs)
- **Redis**: Caching and session data
- **Object Storage (S3/Blob)**: Artifacts, ASTs, analysis results
- **Time-series DB (InfluxDB)**: Metrics and monitoring data

## PostgreSQL Schema

### Core Tables

#### Users and Organizations
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    avatar_url TEXT,
    provider VARCHAR(50) NOT NULL, -- github, gitlab, azure
    provider_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'developer', -- admin, developer, viewer
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    description TEXT,
    avatar_url TEXT,
    provider VARCHAR(50) NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    settings JSONB DEFAULT '{}',
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, pro, enterprise
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Organization memberships
CREATE TABLE organization_members (
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- owner, admin, member, viewer
    permissions JSONB DEFAULT '{}',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (organization_id, user_id)
);
```

#### Repositories
```sql
-- Repositories table
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    description TEXT,
    url TEXT NOT NULL,
    clone_url TEXT NOT NULL,
    provider VARCHAR(50) NOT NULL, -- github, gitlab, azure, bitbucket
    provider_id VARCHAR(255) NOT NULL,
    default_branch VARCHAR(255) DEFAULT 'main',
    visibility VARCHAR(20) DEFAULT 'private', -- public, private, internal
    language_breakdown JSONB DEFAULT '{}',
    size_bytes BIGINT DEFAULT 0,
    scan_config JSONB NOT NULL DEFAULT '{
        "frequency": "daily",
        "include_patterns": ["**/*"],
        "exclude_patterns": ["node_modules/**", ".git/**", "*.min.js"],
        "max_file_size": 10485760,
        "languages": []
    }',
    status VARCHAR(50) DEFAULT 'active', -- active, paused, error, archived
    last_scan_at TIMESTAMP WITH TIME ZONE,
    last_commit_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

-- Repository access control
CREATE TABLE repository_permissions (
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(50) NOT NULL, -- read, write, admin
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (repository_id, user_id)
);
```

#### Analysis and Findings
```sql
-- Scan jobs
CREATE TABLE scan_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    triggered_by UUID REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- full, incremental, differential
    status VARCHAR(50) DEFAULT 'queued', -- queued, running, completed, failed
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    config JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT,
    metrics JSONB DEFAULT '{}'
);

-- Findings
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    scan_job_id UUID REFERENCES scan_jobs(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL, -- code_smell, security, performance, duplicate, architecture
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER,
    column_start INTEGER,
    column_end INTEGER,
    evidence JSONB DEFAULT '{}',
    recommendation JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'new', -- new, acknowledged, resolved, false_positive
    status_comment TEXT,
    status_updated_by UUID REFERENCES users(id),
    status_updated_at TIMESTAMP WITH TIME ZONE,
    hash VARCHAR(64) UNIQUE, -- Content hash for deduplication
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Refactoring Plans
```sql
-- Refactoring plans
CREATE TABLE refactoring_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    findings JSONB DEFAULT '[]', -- Array of finding IDs
    steps JSONB NOT NULL DEFAULT '[]',
    total_risk_score DECIMAL(3,2) CHECK (total_risk_score >= 0 AND total_risk_score <= 1),
    total_effort_estimate INTEGER, -- hours
    status VARCHAR(50) DEFAULT 'draft', -- draft, pending_approval, approved, executing, completed, failed
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    executed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    rollback_plan JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plan execution jobs
CREATE TABLE plan_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES refactoring_plans(id) ON DELETE CASCADE,
    executed_by UUID REFERENCES users(id),
    execution_mode VARCHAR(50) NOT NULL, -- dry_run, create_pr, auto_merge
    branch_strategy VARCHAR(50) DEFAULT 'single_branch',
    status VARCHAR(50) DEFAULT 'queued', -- queued, running, completed, failed
    progress INTEGER DEFAULT 0,
    results JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);
```

#### Configuration and Policies
```sql
-- Safety policies
CREATE TABLE safety_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    scope VARCHAR(50) NOT NULL, -- repository, organization, global
    rules JSONB NOT NULL DEFAULT '[]',
    exceptions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    prefix VARCHAR(20) NOT NULL,
    permissions JSONB DEFAULT '{}',
    rate_limit INTEGER DEFAULT 1000, -- requests per hour
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_repositories_org_status ON repositories(organization_id, status);
CREATE INDEX idx_findings_repo_type_severity ON findings(repository_id, type, severity);
CREATE INDEX idx_findings_status ON findings(status);
CREATE INDEX idx_scan_jobs_repo_status ON scan_jobs(repository_id, status);
CREATE INDEX idx_scan_jobs_created_at ON scan_jobs(created_at);
CREATE INDEX idx_refactoring_plans_repo_status ON refactoring_plans(repository_id, status);

-- Search indexes
CREATE INDEX idx_repositories_name_gin ON repositories USING gin(to_tsvector('english', name || ' ' || coalesce(description, '')));
CREATE INDEX idx_findings_content_gin ON findings USING gin(to_tsvector('english', title || ' ' || coalesce(description, '')));

-- Hash indexes for exact lookups
CREATE INDEX idx_findings_hash ON findings(hash);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
```

## Neo4j Graph Schema

### Node Labels and Properties

#### File Nodes
```cypher
// File nodes represent source code files
CREATE CONSTRAINT file_path_unique FOR (f:File) REQUIRE f.path IS UNIQUE;

// File properties
(:File {
  path: String,           // Unique file path
  name: String,           // File name
  extension: String,      // File extension
  language: String,       // Programming language
  size_bytes: Integer,    // File size
  lines_of_code: Integer, // Total lines
  last_modified: DateTime,
  hash: String,           // Content hash
  repository_id: String   // Reference to repository
})
```

#### Function Nodes
```cypher
// Function/method nodes
CREATE CONSTRAINT function_id_unique FOR (f:Function) REQUIRE f.id IS UNIQUE;

(:Function {
  id: String,                 // Unique identifier
  name: String,              // Function name
  full_name: String,         // Fully qualified name
  signature: String,         // Function signature
  return_type: String,       // Return type
  parameters: [String],      // Parameter list
  visibility: String,        // public, private, protected
  is_static: Boolean,
  is_abstract: Boolean,
  cyclomatic_complexity: Integer,
  cognitive_complexity: Integer,
  lines_of_code: Integer,
  start_line: Integer,
  end_line: Integer,
  file_path: String,
  language: String
})
```

#### Class Nodes
```cypher
// Class/interface/struct nodes
CREATE CONSTRAINT class_id_unique FOR (c:Class) REQUIRE c.id IS UNIQUE;

(:Class {
  id: String,
  name: String,
  full_name: String,
  type: String,              // class, interface, enum, struct
  visibility: String,
  is_abstract: Boolean,
  is_final: Boolean,
  methods_count: Integer,
  fields_count: Integer,
  lines_of_code: Integer,
  start_line: Integer,
  end_line: Integer,
  file_path: String,
  language: String
})
```

#### Variable Nodes
```cypher
// Variable/field nodes
(:Variable {
  id: String,
  name: String,
  type: String,
  scope: String,             // local, instance, class, global
  visibility: String,
  is_constant: Boolean,
  is_static: Boolean,
  line_number: Integer,
  file_path: String
})
```

#### Module Nodes
```cypher
// Module/package/namespace nodes
(:Module {
  id: String,
  name: String,
  full_name: String,
  type: String,              // package, namespace, module
  path: String,
  exports: [String],
  file_count: Integer,
  language: String
})
```

### Relationship Types

#### Containment Relationships
```cypher
// File contains functions, classes, variables
(:File)-[:CONTAINS]->(:Function)
(:File)-[:CONTAINS]->(:Class)
(:File)-[:CONTAINS]->(:Variable)

// Class contains methods and fields
(:Class)-[:CONTAINS]->(:Function)
(:Class)-[:CONTAINS]->(:Variable)

// Module contains files and other modules
(:Module)-[:CONTAINS]->(:File)
(:Module)-[:CONTAINS]->(:Module)
```

#### Call Relationships
```cypher
// Function calls
(:Function)-[:CALLS {
  call_count: Integer,
  call_sites: [Integer]     // Line numbers
}]->(:Function)

// Method invocations
(:Function)-[:INVOKES {
  call_count: Integer,
  call_sites: [Integer]
}]->(:Function)
```

#### Inheritance Relationships
```cypher
// Class inheritance
(:Class)-[:EXTENDS]->(:Class)
(:Class)-[:IMPLEMENTS]->(:Class)

// Interface relationships
(:Class)-[:REALIZES]->(:Class)
```

#### Dependency Relationships
```cypher
// Import/dependency relationships
(:File)-[:IMPORTS {
  import_type: String       // static, dynamic, conditional
}]->(:File)

(:Module)-[:DEPENDS_ON {
  dependency_type: String   // compile, runtime, dev
}]->(:Module)
```

#### Usage Relationships
```cypher
// Variable usage
(:Function)-[:USES {
  access_type: String,      // read, write, read_write
  line_numbers: [Integer]
}]->(:Variable)

// Type usage
(:Function)-[:USES_TYPE]->(:Class)
```

### Graph Queries and Patterns

#### Find Circular Dependencies
```cypher
MATCH path = (m:Module)-[:DEPENDS_ON*2..]->(m)
RETURN path, length(path) as cycle_length
ORDER BY cycle_length
```

#### Identify God Classes
```cypher
MATCH (c:Class)
WHERE c.methods_count > 20 OR c.lines_of_code > 1000
RETURN c.name, c.methods_count, c.lines_of_code, c.file_path
ORDER BY c.methods_count DESC
```

#### Find Unused Functions
```cypher
MATCH (f:Function)
WHERE NOT (f)<-[:CALLS|INVOKES]-()
  AND NOT f.visibility = 'public'
RETURN f.name, f.file_path, f.full_name
```

#### Detect Feature Envy
```cypher
MATCH (f:Function)-[r:CALLS]->(target:Function)
WHERE f.file_path <> target.file_path
WITH f, target.file_path as external_file, count(r) as external_calls
MATCH (f)-[r2:CALLS]->(internal:Function)
WHERE f.file_path = internal.file_path
WITH f, external_file, external_calls, count(r2) as internal_calls
WHERE external_calls > internal_calls
RETURN f.name, f.file_path, external_file, external_calls, internal_calls
```

## Redis Data Structures

### Caching Strategy
```redis
# AST cache (Hash)
HSET ast:{file_hash} content "{ast_json}" ttl 3600

# Symbol table cache (Hash)
HSET symbols:{file_hash} data "{symbols_json}" ttl 3600

# Analysis results cache (Hash)
HSET analysis:{repo_id}:{commit_hash} results "{findings_json}" ttl 86400

# User sessions (Hash with TTL)
HSET session:{session_id} user_id "{user_id}" data "{session_data}"
EXPIRE session:{session_id} 7200

# Rate limiting (String with TTL)
INCR rate_limit:{api_key}:{hour}
EXPIRE rate_limit:{api_key}:{hour} 3600

# Job queues (List)
LPUSH queue:parsing "{job_json}"
LPUSH queue:analysis "{job_json}"
LPUSH queue:planning "{job_json}"

# Real-time notifications (Pub/Sub)
PUBLISH notifications:user:{user_id} "{notification_json}"
PUBLISH notifications:repo:{repo_id} "{event_json}"
```

### Performance Optimization
```redis
# Bloom filters for duplicate detection
BF.ADD duplicates:files:{repo_id} "{file_content_hash}"
BF.EXISTS duplicates:files:{repo_id} "{file_content_hash}"

# HyperLogLog for unique counting
PFADD unique_functions:{repo_id} "{function_signature}"
PFCOUNT unique_functions:{repo_id}

# Sorted sets for ranking
ZADD findings:severity "{severity_score}" "{finding_id}"
ZREVRANGE findings:severity 0 10 WITHSCORES
```

## Object Storage Schema

### Bucket Organization
```
codebase-intelligence/
├── repositories/
│   ├── {org_id}/
│   │   ├── {repo_id}/
│   │   │   ├── snapshots/
│   │   │   │   ├── {commit_hash}.tar.gz
│   │   │   ├── artifacts/
│   │   │   │   ├── asts/
│   │   │   │   │   ├── {file_hash}.json
│   │   │   │   ├── embeddings/
│   │   │   │   │   ├── {file_hash}.vec
│   │   │   │   ├── analysis/
│   │   │   │   │   ├── {scan_id}.json
├── models/
│   ├── embeddings/
│   │   ├── code-bert-v1.bin
│   ├── classifiers/
│   │   ├── risk-prediction-v2.pkl
├── exports/
│   ├── {export_id}/
│   │   ├── data.json
│   │   ├── metadata.json
```

### File Metadata
```json
{
  "bucket": "codebase-intelligence",
  "key": "repositories/org123/repo456/artifacts/asts/abc123.json",
  "content_type": "application/json",
  "size_bytes": 15420,
  "created_at": "2025-01-15T10:30:00Z",
  "checksum": "sha256:d2d2d2d2...",
  "tags": {
    "repository_id": "repo456",
    "file_type": "ast",
    "language": "javascript",
    "retention": "1year"
  },
  "encryption": {
    "algorithm": "AES256",
    "key_id": "arn:aws:kms:us-east-1:123456789:key/abc123"
  }
}
```

## Time-Series Data (InfluxDB)

### Measurement Schemas

#### Repository Metrics
```sql
-- Repository metrics over time
SELECT mean("lines_of_code"), mean("complexity_score"), mean("test_coverage")
FROM "repository_metrics" 
WHERE time >= now() - 30d 
GROUP BY time(1d), "repository_id"
```

#### Performance Metrics
```sql
-- API performance
SELECT mean("response_time"), percentile("response_time", 95)
FROM "api_requests"
WHERE time >= now() - 1h
GROUP BY time(5m), "endpoint", "method"

-- Scan performance
SELECT mean("scan_duration"), count("scans")
FROM "scan_jobs"
WHERE time >= now() - 7d
GROUP BY time(1h), "repository_id", "scan_type"
```

#### Quality Trends
```sql
-- Code quality trends
SELECT mean("technical_debt_ratio"), mean("duplication_percentage")
FROM "quality_metrics"
WHERE time >= now() - 90d
GROUP BY time(1d), "repository_id"
```

## Data Consistency and Integrity

### ACID Transactions
```sql
-- Example: Creating a refactoring plan with findings
BEGIN;
  INSERT INTO refactoring_plans (...) VALUES (...);
  UPDATE findings SET status = 'included_in_plan' WHERE id = ANY($1);
  INSERT INTO audit_log (action, entity_type, entity_id, user_id) 
    VALUES ('plan_created', 'refactoring_plan', $plan_id, $user_id);
COMMIT;
```

### Data Validation
```sql
-- Triggers for data validation
CREATE OR REPLACE FUNCTION validate_finding_location()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.line_end IS NOT NULL AND NEW.line_end < NEW.line_start THEN
    RAISE EXCEPTION 'line_end must be >= line_start';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_finding_location_trigger
  BEFORE INSERT OR UPDATE ON findings
  FOR EACH ROW EXECUTE FUNCTION validate_finding_location();
```

### Data Retention Policies
```sql
-- Automated cleanup of old data
DELETE FROM scan_jobs 
WHERE status = 'completed' 
  AND created_at < NOW() - INTERVAL '90 days';

DELETE FROM audit_log 
WHERE created_at < NOW() - INTERVAL '2 years';
```