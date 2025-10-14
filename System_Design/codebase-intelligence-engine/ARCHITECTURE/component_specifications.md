# Component Specifications

## 1. Ingestion Service

### Purpose
Manages repository discovery, cloning, and incremental updates from various Git providers.

### Responsibilities
- Repository registration and authentication
- Full and incremental repository scanning
- File change detection and delta processing
- Metadata extraction (contributors, commit history, file stats)
- Git provider API integration

### Interfaces

#### REST API Endpoints
```
POST /api/v1/repositories
GET /api/v1/repositories/{id}
PUT /api/v1/repositories/{id}
DELETE /api/v1/repositories/{id}
POST /api/v1/repositories/{id}/scan
GET /api/v1/repositories/{id}/scan-status
```

#### Message Queue Events
```
Publishes:
- repository.cloned
- repository.updated
- files.changed
- scan.completed

Subscribes:
- repository.registered
- webhook.received
```

### Data Model
```json
{
  "repository": {
    "id": "uuid",
    "name": "string",
    "url": "string",
    "provider": "github|gitlab|azure",
    "credentials": "encrypted_string",
    "scan_config": {
      "frequency": "hourly|daily|weekly",
      "include_patterns": ["string"],
      "exclude_patterns": ["string"],
      "max_file_size": "integer"
    },
    "last_scan": "timestamp",
    "status": "active|paused|error"
  }
}
```

### Configuration
- Git provider credentials and API limits
- Scan scheduling and concurrency settings
- File filtering rules and size limits
- Webhook endpoint configurations

### Dependencies
- Git providers (GitHub, GitLab, Azure DevOps)
- Object storage for repository snapshots
- Message queue for event publishing
- Database for repository metadata

---

## 2. Parser Service

### Purpose
Language-aware parsing of source code files to generate Abstract Syntax Trees (ASTs) and extract semantic information.

### Responsibilities
- Language detection and parser selection
- AST generation and normalization
- Symbol table extraction
- Type information gathering
- Comment and documentation parsing
- Cross-reference resolution

### Interfaces

#### REST API Endpoints
```
POST /api/v1/parse/file
POST /api/v1/parse/batch
GET /api/v1/parse/status/{job_id}
GET /api/v1/languages/supported
```

#### Message Queue Events
```
Publishes:
- file.parsed
- symbols.extracted
- ast.generated
- parsing.failed

Subscribes:
- files.changed
- parse.requested
```

### Supported Languages
- **Tier 1**: JavaScript/TypeScript, Python, Java, C#, Go
- **Tier 2**: C/C++, Rust, Kotlin, Swift, Ruby
- **Tier 3**: PHP, Scala, Perl, R, MATLAB

### Parser Architecture
```
File Input → Language Detection → Parser Selection → AST Generation → Symbol Extraction → Normalization → Output
```

### Data Model
```json
{
  "parsed_file": {
    "file_path": "string",
    "language": "string",
    "parser_version": "string",
    "ast": "json_object",
    "symbols": [{
      "name": "string",
      "type": "function|class|variable|import",
      "location": {
        "line": "integer",
        "column": "integer",
        "end_line": "integer",
        "end_column": "integer"
      },
      "scope": "string",
      "references": ["location"]
    }],
    "imports": ["string"],
    "exports": ["string"],
    "complexity_metrics": {
      "cyclomatic": "integer",
      "cognitive": "integer",
      "lines_of_code": "integer"
    }
  }
}
```

### Performance Requirements
- Process 1000+ files per minute
- Support files up to 10MB
- Memory usage under 2GB per worker
- Cache ASTs for unchanged files

---

## 3. Code Intelligence Graph Service

### Purpose
Maintains a comprehensive graph database of code entities, relationships, and metadata across the entire codebase.

### Responsibilities
- Graph schema management and evolution
- Entity creation and relationship mapping
- Query optimization and indexing
- Graph traversal and pathfinding
- Subgraph extraction for analysis
- Graph-based metrics computation

### Graph Schema

#### Node Types
```
File: file_path, language, size, last_modified
Function: name, signature, complexity, lines_of_code
Class: name, inheritance_chain, interface_implementations
Variable: name, type, scope, mutability
Module: name, namespace, exports
Import: source, target, type
```

#### Relationship Types
```
CONTAINS: File → Function/Class/Variable
CALLS: Function → Function
INHERITS: Class → Class
IMPLEMENTS: Class → Interface
USES: Function → Variable
IMPORTS: Module → Module
DEPENDS_ON: File → File
```

### Interfaces

#### GraphQL API
```graphql
type Query {
  files(filter: FileFilter): [File]
  functions(filter: FunctionFilter): [Function]
  dependencies(from: String!, depth: Int): [Dependency]
  findPaths(from: String!, to: String!): [Path]
  metrics(scope: String!): Metrics
}

type Mutation {
  updateNode(id: ID!, data: NodeData!): Node
  createRelationship(from: ID!, to: ID!, type: String!): Relationship
}
```

#### REST API Endpoints
```
GET /api/v1/graph/nodes/{id}
GET /api/v1/graph/relationships
POST /api/v1/graph/query
GET /api/v1/graph/metrics
POST /api/v1/graph/subgraph
```

### Query Patterns
```cypher
// Find all functions calling a specific function
MATCH (caller:Function)-[:CALLS]->(target:Function {name: $name})
RETURN caller

// Detect circular dependencies
MATCH path = (m1:Module)-[:DEPENDS_ON*]->(m1)
RETURN path

// Find orphaned code
MATCH (f:Function)
WHERE NOT (f)<-[:CALLS]-()
RETURN f
```

### Performance Requirements
- Query response time < 100ms for simple queries
- Support graphs with 10M+ nodes and 100M+ relationships
- Concurrent read operations: 1000+ QPS
- Write operations: 10,000+ updates per minute

---

## 4. AI Analysis Engine

### Purpose
Applies machine learning and rule-based analysis to detect code smells, anti-patterns, duplicates, and architectural issues.

### Responsibilities
- Code smell detection and classification
- Duplicate/clone detection using embeddings
- Architectural drift identification
- Risk scoring and prioritization
- Test coverage gap analysis
- Performance hotspot detection

### Analysis Modules

#### Rule-Based Analyzers
- **Code Smells**: Long methods, large classes, data clumps
- **Anti-patterns**: God objects, spaghetti code, magic numbers
- **Security**: SQL injection, XSS vulnerabilities, hardcoded secrets
- **Performance**: N+1 queries, inefficient algorithms

#### ML-Based Analyzers
- **Clone Detection**: Semantic similarity using code embeddings
- **Risk Prediction**: Defect probability based on historical data
- **Effort Estimation**: Time to fix based on complexity metrics
- **Quality Scoring**: Overall code quality assessment

### Interfaces

#### REST API Endpoints
```
POST /api/v1/analyze/repository/{id}
GET /api/v1/analyze/results/{job_id}
POST /api/v1/analyze/file
GET /api/v1/analyze/metrics/{repository_id}
```

#### Message Queue Events
```
Publishes:
- analysis.completed
- findings.generated
- risk.scored
- duplicates.detected

Subscribes:
- ast.generated
- analyze.requested
```

### Analysis Pipeline
```
Input (AST + Graph) → Feature Extraction → Rule Engine → ML Models → Scoring → Finding Generation → Output
```

### Data Model
```json
{
  "finding": {
    "id": "uuid",
    "type": "code_smell|security|performance|duplicate",
    "severity": "critical|high|medium|low",
    "confidence": "float[0-1]",
    "title": "string",
    "description": "string",
    "location": {
      "file": "string",
      "line_start": "integer",
      "line_end": "integer"
    },
    "evidence": {
      "metrics": "object",
      "similar_code": ["location"],
      "rule_id": "string"
    },
    "recommendation": {
      "action": "string",
      "effort_estimate": "integer_hours",
      "priority": "integer"
    }
  }
}
```

### ML Models
- **Code Embeddings**: CodeBERT/GraphCodeBERT for semantic understanding
- **Risk Classifier**: Random Forest for defect prediction
- **Similarity Model**: Siamese networks for clone detection
- **Quality Regressor**: Neural network for quality scoring

---

## 5. Refactoring Planner

### Purpose
Generates safe, incremental refactoring plans based on analysis findings and impact assessment.

### Responsibilities
- Refactoring opportunity identification
- Impact analysis and dependency tracking
- Change planning and sequencing
- Diff generation and preview
- Risk assessment for proposed changes
- Rollback plan creation

### Planning Algorithms

#### Change Impact Analysis
```
function analyzeImpact(change) {
  1. Identify affected nodes in graph
  2. Trace dependencies and callers
  3. Estimate test coverage impact
  4. Calculate risk score
  5. Generate dependency order
}
```

#### Refactoring Types
- **Extract Method**: Break down large functions
- **Rename**: Improve naming consistency
- **Move Class**: Reorganize package structure
- **Remove Duplicates**: Consolidate similar code
- **Update Dependencies**: Upgrade outdated libraries

### Interfaces

#### REST API Endpoints
```
POST /api/v1/plan/generate
GET /api/v1/plan/{id}
POST /api/v1/plan/{id}/execute
GET /api/v1/plan/{id}/preview
POST /api/v1/plan/{id}/rollback
```

### Data Model
```json
{
  "refactoring_plan": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "findings": ["finding_id"],
    "steps": [{
      "id": "integer",
      "type": "extract|rename|move|remove",
      "description": "string",
      "files": ["string"],
      "changes": [{
        "file": "string",
        "operation": "add|modify|delete",
        "content": "string",
        "line_number": "integer"
      }],
      "dependencies": ["step_id"],
      "risk_score": "float[0-1]",
      "estimated_effort": "integer_hours"
    }],
    "total_risk": "float[0-1]",
    "total_effort": "integer_hours",
    "rollback_plan": "object"
  }
}
```

### Safety Constraints
- Maximum files changed per plan: 50
- Maximum lines changed per file: 500
- No changes to critical/protected paths
- Maintain backward compatibility
- Preserve test coverage levels

---

## 6. Safety Engine

### Purpose
Implements safety gates, validation checks, and governance policies to ensure proposed changes are safe and compliant.

### Responsibilities
- Policy definition and enforcement
- Validation gate orchestration
- Test execution coordination
- Approval workflow management
- Rollback monitoring and automation
- Compliance reporting

### Safety Gates

#### Pre-change Validation
```
1. Policy Check → CODEOWNERS validation
2. Impact Assessment → Risk threshold check
3. Test Coverage → Minimum coverage requirement
4. Security Scan → Vulnerability detection
5. Build Verification → Compilation check
```

#### Post-change Monitoring
```
1. Deployment Health → Service availability
2. Performance Impact → Latency/throughput monitoring
3. Error Rate → Exception tracking
4. Business Metrics → Key performance indicators
```

### Interfaces

#### REST API Endpoints
```
POST /api/v1/safety/validate
GET /api/v1/safety/policies
POST /api/v1/safety/policies
GET /api/v1/safety/status/{plan_id}
POST /api/v1/safety/approve/{plan_id}
```

### Policy Engine
```json
{
  "policy": {
    "name": "string",
    "scope": "repository|organization|global",
    "rules": [{
      "type": "approval|validation|gate",
      "condition": "string",
      "action": "block|warn|require_approval"
    }],
    "exceptions": [{
      "path_pattern": "string",
      "reason": "string",
      "expires": "timestamp"
    }]
  }
}
```

### Validation Pipeline
```
Policy Engine → Test Execution → Security Scan → Build Check → Approval Workflow → Deployment Gate
```