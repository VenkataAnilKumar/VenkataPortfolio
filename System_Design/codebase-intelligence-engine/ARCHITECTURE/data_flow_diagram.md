# Data Flow Architecture Diagram

## Overview
This diagram illustrates the complete data flow through the Codebase Intelligence Engine, from repository ingestion to refactoring plan execution.

```mermaid
flowchart TD
    subgraph "Input Sources"
        REPO[📁 Repository<br/>Source Code]
        WEBHOOK[🔔 Git Webhooks<br/>Change Events]
        MANUAL[👤 Manual Trigger<br/>User Request]
    end

    subgraph "Ingestion Layer"
        CLONE[📥 Repository Clone<br/>Git Operations]
        DIFF[📊 Change Detection<br/>Delta Analysis]
        FILE_DISCOVERY[🔍 File Discovery<br/>Language Detection]
    end

    subgraph "Parsing & Analysis"
        LANGUAGE_DETECT[🏷️ Language Detection<br/>File Type Analysis]
        PARSER_SELECT[⚙️ Parser Selection<br/>Strategy Pattern]
        AST_GEN[🌳 AST Generation<br/>Syntax Trees]
        SYMBOL_EXTRACT[🔤 Symbol Extraction<br/>Identifiers & References]
        METRICS_CALC[📏 Metrics Calculation<br/>Complexity & Quality]
    end

    subgraph "Graph Construction"
        NODE_CREATE[🔵 Node Creation<br/>Files, Functions, Classes]
        EDGE_CREATE[🔗 Edge Creation<br/>Dependencies, Calls]
        GRAPH_INDEX[📚 Graph Indexing<br/>Search Optimization]
        GRAPH_VALIDATE[✅ Graph Validation<br/>Consistency Checks]
    end

    subgraph "AI Analysis Pipeline"
        FEATURE_EXTRACT[🎯 Feature Extraction<br/>Code Patterns]
        EMBEDDING_GEN[🧮 Embedding Generation<br/>Vector Representations]
        PATTERN_DETECT[🔍 Pattern Detection<br/>Code Smells & Anti-patterns]
        RISK_SCORING[⚠️ Risk Scoring<br/>Vulnerability Assessment]
        DUPLICATE_DETECT[👯 Duplicate Detection<br/>Clone Analysis]
    end

    subgraph "Planning & Recommendations"
        OPPORTUNITY_ID[💡 Opportunity Identification<br/>Refactoring Candidates]
        IMPACT_ANALYSIS[📊 Impact Analysis<br/>Change Scope Assessment]
        DEPENDENCY_ANALYSIS[🕸️ Dependency Analysis<br/>Safe Order Planning]
        PLAN_GENERATION[📋 Plan Generation<br/>Step-by-Step Changes]
        EFFORT_ESTIMATION[⏱️ Effort Estimation<br/>Time & Resource Calc]
    end

    subgraph "Safety & Validation"
        POLICY_CHECK[🛡️ Policy Check<br/>Governance Rules]
        SAFETY_GATE[🚧 Safety Gates<br/>Approval Requirements]
        TEST_VALIDATION[🧪 Test Validation<br/>Coverage Analysis]
        BUILD_CHECK[🔨 Build Check<br/>Compilation Verification]
        SECURITY_SCAN[🔒 Security Scan<br/>Vulnerability Check]
    end

    subgraph "Execution & Delivery"
        DIFF_GENERATION[📝 Diff Generation<br/>Change Sets]
        PR_CREATION[🔄 PR Creation<br/>Pull Request]
        BRANCH_STRATEGY[🌿 Branch Strategy<br/>Feature/Step Branches]
        NOTIFICATION[📢 Notification<br/>Alerts & Updates]
        FEEDBACK_LOOP[🔄 Feedback Loop<br/>Learning & Improvement]
    end

    subgraph "Data Storage"
        CACHE[(⚡ Cache<br/>Redis)]
        METADATA[(🐘 Metadata<br/>PostgreSQL)]
        GRAPH_DB[(🔗 Graph<br/>Neo4j)]
        ARTIFACTS[(📦 Artifacts<br/>Object Storage)]
        METRICS_DB[(📊 Metrics<br/>InfluxDB)]
    end

    subgraph "Message Queue"
        QUEUE[📬 Event Queue<br/>Processing Pipeline]
    end

    %% Input flow
    REPO --> CLONE
    WEBHOOK --> DIFF
    MANUAL --> CLONE
    
    %% Ingestion flow
    CLONE --> FILE_DISCOVERY
    DIFF --> FILE_DISCOVERY
    FILE_DISCOVERY --> LANGUAGE_DETECT
    
    %% Parsing flow
    LANGUAGE_DETECT --> PARSER_SELECT
    PARSER_SELECT --> AST_GEN
    AST_GEN --> SYMBOL_EXTRACT
    SYMBOL_EXTRACT --> METRICS_CALC
    
    %% Graph construction flow
    METRICS_CALC --> NODE_CREATE
    NODE_CREATE --> EDGE_CREATE
    EDGE_CREATE --> GRAPH_INDEX
    GRAPH_INDEX --> GRAPH_VALIDATE
    
    %% AI analysis flow
    GRAPH_VALIDATE --> FEATURE_EXTRACT
    FEATURE_EXTRACT --> EMBEDDING_GEN
    EMBEDDING_GEN --> PATTERN_DETECT
    PATTERN_DETECT --> RISK_SCORING
    RISK_SCORING --> DUPLICATE_DETECT
    
    %% Planning flow
    DUPLICATE_DETECT --> OPPORTUNITY_ID
    OPPORTUNITY_ID --> IMPACT_ANALYSIS
    IMPACT_ANALYSIS --> DEPENDENCY_ANALYSIS
    DEPENDENCY_ANALYSIS --> PLAN_GENERATION
    PLAN_GENERATION --> EFFORT_ESTIMATION
    
    %% Safety flow
    EFFORT_ESTIMATION --> POLICY_CHECK
    POLICY_CHECK --> SAFETY_GATE
    SAFETY_GATE --> TEST_VALIDATION
    TEST_VALIDATION --> BUILD_CHECK
    BUILD_CHECK --> SECURITY_SCAN
    
    %% Execution flow
    SECURITY_SCAN --> DIFF_GENERATION
    DIFF_GENERATION --> PR_CREATION
    PR_CREATION --> BRANCH_STRATEGY
    BRANCH_STRATEGY --> NOTIFICATION
    NOTIFICATION --> FEEDBACK_LOOP
    
    %% Queue connections
    FILE_DISCOVERY --> QUEUE
    METRICS_CALC --> QUEUE
    DUPLICATE_DETECT --> QUEUE
    EFFORT_ESTIMATION --> QUEUE
    
    QUEUE --> LANGUAGE_DETECT
    QUEUE --> FEATURE_EXTRACT
    QUEUE --> OPPORTUNITY_ID
    QUEUE --> POLICY_CHECK
    
    %% Storage connections
    AST_GEN --> CACHE
    SYMBOL_EXTRACT --> ARTIFACTS
    GRAPH_VALIDATE --> GRAPH_DB
    PATTERN_DETECT --> METADATA
    PLAN_GENERATION --> METADATA
    NOTIFICATION --> METRICS_DB
    
    %% Feedback connections
    FEEDBACK_LOOP -.-> FEATURE_EXTRACT
    FEEDBACK_LOOP -.-> PATTERN_DETECT
    FEEDBACK_LOOP -.-> RISK_SCORING
    
    %% Styling
    classDef input fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
    classDef ingestion fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef parsing fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef graph fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef ai fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef planning fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef safety fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef execution fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    classDef storage fill:#f9fbe7,stroke:#689f38,stroke-width:2px
    classDef queue fill:#fff8e1,stroke:#f57c00,stroke-width:2px
    
    class REPO,WEBHOOK,MANUAL input
    class CLONE,DIFF,FILE_DISCOVERY ingestion
    class LANGUAGE_DETECT,PARSER_SELECT,AST_GEN,SYMBOL_EXTRACT,METRICS_CALC parsing
    class NODE_CREATE,EDGE_CREATE,GRAPH_INDEX,GRAPH_VALIDATE graph
    class FEATURE_EXTRACT,EMBEDDING_GEN,PATTERN_DETECT,RISK_SCORING,DUPLICATE_DETECT ai
    class OPPORTUNITY_ID,IMPACT_ANALYSIS,DEPENDENCY_ANALYSIS,PLAN_GENERATION,EFFORT_ESTIMATION planning
    class POLICY_CHECK,SAFETY_GATE,TEST_VALIDATION,BUILD_CHECK,SECURITY_SCAN safety
    class DIFF_GENERATION,PR_CREATION,BRANCH_STRATEGY,NOTIFICATION,FEEDBACK_LOOP execution
    class CACHE,METADATA,GRAPH_DB,ARTIFACTS,METRICS_DB storage
    class QUEUE queue
```

## Data Flow Phases

### 1. **Ingestion Phase** 📥
- **Repository Cloning**: Full or incremental repository snapshots
- **Change Detection**: Git diff analysis for incremental updates
- **File Discovery**: Recursive file system traversal with filtering
- **Language Detection**: MIME type and extension-based classification

**Output**: Structured file inventory with metadata

### 2. **Parsing Phase** 🔍
- **Parser Selection**: Language-specific AST generators (Tree-sitter, Babel, etc.)
- **AST Generation**: Abstract syntax tree creation with position mapping
- **Symbol Extraction**: Identifiers, references, and scope analysis
- **Metrics Calculation**: Complexity, maintainability, and quality metrics

**Output**: Enriched ASTs with symbol tables and metrics

### 3. **Graph Construction Phase** 🕸️
- **Node Creation**: File, function, class, and variable entities
- **Edge Creation**: Call graphs, inheritance, dependencies, and usage
- **Graph Indexing**: Performance optimization for queries
- **Validation**: Consistency checks and constraint verification

**Output**: Code Intelligence Graph ready for analysis

### 4. **AI Analysis Phase** 🧠
- **Feature Extraction**: Statistical and structural code features
- **Embedding Generation**: Dense vector representations using CodeBERT
- **Pattern Detection**: Rule-based and ML-based smell detection
- **Risk Scoring**: Defect probability and maintainability assessment
- **Duplicate Detection**: Semantic and syntactic clone identification

**Output**: Findings with confidence scores and evidence

### 5. **Planning Phase** 📋
- **Opportunity Identification**: Refactoring candidate selection
- **Impact Analysis**: Change scope and affected components
- **Dependency Analysis**: Safe execution order determination
- **Plan Generation**: Step-by-step refactoring workflow
- **Effort Estimation**: Time and resource requirements

**Output**: Executable refactoring plans with risk assessment

### 6. **Safety & Validation Phase** 🛡️
- **Policy Enforcement**: Governance rules and constraints
- **Safety Gates**: Approval workflows and manual checkpoints
- **Test Validation**: Coverage requirements and test execution
- **Build Verification**: Compilation and static analysis checks
- **Security Scanning**: Vulnerability and secret detection

**Output**: Validated and approved execution plans

### 7. **Execution & Delivery Phase** 🚀
- **Diff Generation**: Precise change sets with context
- **PR Creation**: Pull request generation with descriptions
- **Branch Strategy**: Feature branches or atomic commits
- **Notification**: Real-time updates to stakeholders
- **Feedback Integration**: Learning from user interactions

**Output**: Executed changes with monitoring and rollback capability

## Performance Characteristics

| Phase | Processing Time | Scalability | Caching Strategy |
|-------|----------------|-------------|------------------|
| Ingestion | 10-30 seconds | Horizontal workers | Repository snapshots |
| Parsing | 1-5 minutes | Language-specific pools | AST cache by file hash |
| Graph Construction | 30 seconds - 2 minutes | Graph database sharding | Subgraph materialization |
| AI Analysis | 2-10 minutes | GPU acceleration | Feature vector cache |
| Planning | 30 seconds - 2 minutes | Parallel plan generation | Impact analysis cache |
| Safety & Validation | 1-5 minutes | Pipeline parallelization | Validation result cache |
| Execution | 5-30 seconds | Async PR creation | Diff template cache |

## Error Handling & Recovery

- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breakers**: Prevent cascade failures across services
- **Dead Letter Queues**: Failed message handling and analysis
- **Partial Processing**: Continue with available data when possible
- **Rollback Capability**: Automatic recovery from validation failures
- **Manual Intervention**: Human oversight for complex scenarios