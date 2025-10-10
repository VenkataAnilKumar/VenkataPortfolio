import os
from functools import lru_cache
from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List


class Environment(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class Settings(BaseModel):
    # Environment settings
    env: Environment = Field(
        Environment(os.getenv("ENV", "dev")),
        description="Current environment (dev/staging/prod)"
    )
    # Database settings
    db_url: str = Field(
        os.getenv("DB_URL", "sqlite+aiosqlite:///./disputes.db"),
        description="Database connection URL"
    )
    redis_url: str = Field(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        description="Redis cache connection URL"
    )
    
    # LLM settings
    llm_provider: LLMProvider = Field(
        LLMProvider(os.getenv("LLM_PROVIDER", "openai")),
        description="Primary LLM provider"
    )
    mock_llm: bool = Field(
        os.getenv("MOCK_LLM", "0") == "1",
        description="Use mock LLM for testing"
    )
    openai_api_key: Optional[str] = Field(
        os.getenv("OPENAI_API_KEY"),
        description="OpenAI API key"
    )
    anthropic_api_key: Optional[str] = Field(
        os.getenv("ANTHROPIC_API_KEY"),
        description="Anthropic API key"
    )
    model_config: Dict[str, str] = Field(
        {
            "classification": "gpt-4-1106-preview",
            "recommendation": "gpt-4-1106-preview",
            "pattern": "claude-2.1",
            "backup": "gpt-3.5-turbo-1106"
        },
        description="Model configurations per task"
    )
    
    # API settings
    api_key: str = Field(
        os.getenv("API_KEY", "changeme"),
        description="API authentication key"
    )
    jwt_secret: str = Field(
        os.getenv("JWT_SECRET", "changeme"),
        description="JWT signing secret"
    )
    cors_origins: List[str] = Field(
        os.getenv("CORS_ORIGINS", "*").split(","),
        description="Allowed CORS origins"
    )
    
    # Performance settings
    token_budget_per_case: int = Field(
        int(os.getenv("TOKEN_BUDGET_PER_CASE", "8000")),
        description="Max tokens per case",
        ge=1000,
        le=16000
    )
    max_concurrent_llm_calls: int = Field(
        int(os.getenv("MAX_CONCURRENT_LLM_CALLS", "10")),
        description="Max concurrent LLM API calls",
        ge=1,
        le=50
    )
    llm_timeout_seconds: int = Field(
        int(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        description="LLM API timeout in seconds",
        ge=1,
        le=300
    )
    cache_ttl_seconds: int = Field(
        int(os.getenv("CACHE_TTL_SECONDS", "3600")),
        description="Cache TTL in seconds",
        ge=60
    )
    
    # Security settings
    enable_pii_redaction: bool = Field(
        os.getenv("ENABLE_PII_REDACTION", "1") == "1",
        description="Enable PII detection and redaction"
    )
    pii_confidence_threshold: float = Field(
        float(os.getenv("PII_CONFIDENCE_THRESHOLD", "0.7")),
        description="PII detection confidence threshold",
        ge=0.0,
        le=1.0
    )
    max_narrative_length: int = Field(
        int(os.getenv("MAX_NARRATIVE_LENGTH", "10000")),
        description="Max narrative text length",
        ge=100,
        le=50000
    )
    rate_limit_per_minute: int = Field(
        int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
        description="API rate limit per minute",
        ge=1
    )
    
    # Analytics settings
    enable_pattern_detection: bool = Field(
        os.getenv("ENABLE_PATTERN_DETECTION", "1") == "1",
        description="Enable fraud pattern detection"
    )
    pattern_detection_window_days: int = Field(
        int(os.getenv("PATTERN_DETECTION_WINDOW_DAYS", "30")),
        description="Pattern detection lookback window",
        ge=1,
        le=365
    )
    risk_score_threshold: float = Field(
        float(os.getenv("RISK_SCORE_THRESHOLD", "0.8")),
        description="Risk score alert threshold",
        ge=0.0,
        le=1.0
    )
    
    # Telemetry settings
    enable_prometheus: bool = Field(
        os.getenv("ENABLE_PROMETHEUS", "1") == "1",
        description="Enable Prometheus metrics"
    )
    metrics_port: int = Field(
        int(os.getenv("METRICS_PORT", "9090")),
        description="Prometheus metrics port"
    )
    enable_audit_logging: bool = Field(
        os.getenv("ENABLE_AUDIT_LOGGING", "1") == "1",
        description="Enable detailed audit logging"
    )
    
    # Feature flags
    enable_advanced_enrichment: bool = Field(
        os.getenv("ENABLE_ADVANCED_ENRICHMENT", "1") == "1",
        description="Enable advanced data enrichment"
    )
    enable_real_time_alerts: bool = Field(
        os.getenv("ENABLE_REAL_TIME_ALERTS", "1") == "1",
        description="Enable real-time alert system"
    )
    enable_auto_resolution: bool = Field(
        os.getenv("ENABLE_AUTO_RESOLUTION", "0") == "1",
        description="Enable automatic dispute resolution"
    )
    
    @validator("model_config")
    def validate_model_config(cls, v):
        required_tasks = {"classification", "recommendation", "pattern"}
        if not all(task in v for task in required_tasks):
            raise ValueError(f"Missing required model configs: {required_tasks}")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
