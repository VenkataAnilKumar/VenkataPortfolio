from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_client import start_http_server

from app.api.routers import disputes, disputes_v1, analytics
from app.infra.db import init_db
from app.telemetry.metrics import metrics, audit
from app.security.pii_handler import PIIHandler
from app.security.auth import SecurityManager
from app.analytics.engine import AnalyticsEngine
from app.core.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await init_db()
    
    # Start Prometheus metrics server
    if settings.enable_prometheus:
        start_http_server(settings.metrics_port)
        
    # Initialize components
    app.state.security = SecurityManager()
    app.state.pii_handler = PIIHandler()
    app.state.analytics = AnalyticsEngine()
    
    yield
    
    # Shutdown - cleanup if needed
    pass

app = FastAPI(
    title="LLM Dispute Resolution System",
    description="Enterprise-grade dispute resolution system with advanced analytics and security",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security and audit middleware."""
    try:
        # Skip auth for docs and metrics
        if request.url.path in ["/docs", "/redoc", "/metrics", "/health"]:
            return await call_next(request)
            
        # Verify API key
        if request.url.path.startswith("/v1"):
            key = request.headers.get("x-api-key")
            if key != settings.api_key:
                audit.log_security(
                    event_type="AUTH_FAILURE",
                    severity="HIGH",
                    description="Invalid API key"
                )
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid API key"}
                )
                
        # Check rate limits
        await app.state.security.check_rate_limit(
            key=request.headers.get("x-api-key", "anonymous")
        )
        
        # Process request
        response = await call_next(request)
        
        # Log success
        audit.log_access(
            user_id=request.headers.get("x-api-key", "anonymous"),
            resource=request.url.path,
            action=request.method,
            status="SUCCESS"
        )
        
        return response
        
    except Exception as e:
        # Log error
        audit.log_access(
            user_id=request.headers.get("x-api-key", "anonymous"),
            resource=request.url.path,
            action=request.method,
            status="ERROR",
            details={"error": str(e)}
        )
        raise

# Register routes
app.include_router(disputes_v1.router)   # API v1 routes
app.include_router(analytics.router)     # Analytics routes

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "security": "operational",
            "analytics": "operational",
            "telemetry": "operational"
        }
    }

@app.get("/")
async def root():
    return {
        "message": "LLM Dispute Resolution System", 
        "version": "2.0.0",
        "features": [
            "Multi-agent dispute processing",
            "Real LLM integration",
            "PII redaction and security",
            "Advanced pattern detection",
            "Fraud analytics",
            "Merchant risk scoring"
        ],
        "endpoints": {
            "disputes": "/v1/disputes",
            "analytics": "/v1/analytics",
            "metrics": "/v1/metrics",
            "docs": "/docs"
        }
    }

# Include routers
app.include_router(disputes.router)      # Legacy v0 API
app.include_router(disputes_v1.router)   # Enhanced v1 API 
app.include_router(analytics.router)     # Advanced analytics API
app.include_router(metrics_router)       # System metrics
