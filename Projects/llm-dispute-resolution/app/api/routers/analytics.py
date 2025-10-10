"""
Advanced Analytics Router.
Provides comprehensive analytics, risk assessment, and fraud detection endpoints.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field

from app.security.auth import SecurityManager, TokenData
from app.analytics.engine import AnalyticsEngine, PatternDetector, RiskScorer
from app.services.db import DatabaseService
from app.security.pii_handler import PIIHandler
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/v1/analytics", tags=["analytics"])
security = SecurityManager()
analytics = AnalyticsEngine()
db = DatabaseService()
pii_handler = PIIHandler()

# Response Models
class PatternResponse(BaseModel):
    """Pattern detection response."""
    type: str
    severity: str
    description: str
    confidence: float
    metadata: Dict = Field(default_factory=dict)

class MerchantRiskResponse(BaseModel):
    """Merchant risk assessment response"""
    merchant_id: str
    risk_score: float
    risk_level: str
    factors: Dict[str, Any]
    stats: Dict[str, Any]

class PIIAnalysisResponse(BaseModel):
    """PII analysis response"""
    original_text: str
    redacted_text: str
    pii_detected: bool
    pii_summary: Dict[str, int]
    redaction_count: int
    detected_types: List[str]

class LLMUsageResponse(BaseModel):
    """LLM usage statistics response"""
    total_cost: float
    total_tokens: int
    provider_stats: Dict[str, Any]

@router.get("/patterns", response_model=List[PatternAlertResponse])
async def get_pattern_alerts(
    days_back: int = Query(30, ge=1, le=90, description="Days to analyze"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type")
):
    """
    Analyze dispute patterns and return alerts for suspicious activity
    
    This endpoint uses advanced statistical analysis to detect:
    - Fraud clusters by merchant
    - Unusual customer behavior
    - Temporal anomalies
    - Amount-based suspicious patterns
    """
    try:
        alerts = await pattern_engine.analyze_dispute_patterns(days_back)
        
        # Apply filters
        if severity:
            try:
                severity_enum = AlertSeverity(severity.lower())
                alerts = [alert for alert in alerts if alert.severity == severity_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        if pattern_type:
            try:
                pattern_enum = PatternType(pattern_type.lower())
                alerts = [alert for alert in alerts if alert.pattern_type == pattern_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid pattern type: {pattern_type}")
        
        # Convert to response format
        return [
            PatternAlertResponse(
                id=alert.id,
                pattern_type=alert.pattern_type.value,
                severity=alert.severity.value,
                title=alert.title,
                description=alert.description,
                entities_involved=alert.entities_involved,
                confidence_score=alert.confidence_score,
                detected_at=alert.detected_at,
                metadata=alert.metadata
            )
            for alert in alerts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@router.get("/merchants/{merchant_id}/risk", response_model=MerchantRiskResponse)
async def get_merchant_risk_score(
    merchant_id: str,
    days_back: int = Query(30, ge=1, le=90, description="Days to analyze")
):
    """
    Calculate comprehensive risk score for a specific merchant
    
    Risk scoring considers:
    - Fraud rate in disputes
    - Dispute frequency
    - Customer diversity
    - Historical patterns
    """
    try:
        risk_data = await pattern_engine.get_merchant_risk_score(merchant_id, days_back)
        return MerchantRiskResponse(**risk_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@router.post("/pii/analyze", response_model=PIIAnalysisResponse)
async def analyze_pii(text: str):
    """
    Analyze text for PII content and show redaction preview
    
    This endpoint helps understand what PII would be redacted
    before sending text to LLM providers for processing.
    """
    try:
        # Detect PII
        pii_matches = pii_redactor.detect_pii(text)
        
        # Generate redacted version
        redacted_text, _ = pii_redactor.redact_text(text)
        
        # Create summary
        pii_summary = pii_redactor.get_redaction_summary(pii_matches)
        detected_types = list(set(match.pii_type.value for match in pii_matches))
        
        return PIIAnalysisResponse(
            original_text=text,
            redacted_text=redacted_text,
            pii_detected=len(pii_matches) > 0,
            pii_summary=pii_summary,
            redaction_count=len(pii_matches),
            detected_types=detected_types
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PII analysis failed: {str(e)}")

@router.get("/llm/usage", response_model=LLMUsageResponse)
async def get_llm_usage_stats():
    """
    Get current LLM usage statistics including costs and token consumption
    
    Useful for monitoring and cost optimization.
    """
    try:
        stats = llm_adapter.get_usage_stats()
        
        return LLMUsageResponse(
            total_cost=stats.get("total_cost", 0.0),
            total_tokens=stats.get("total_tokens", 0),
            provider_stats={
                "mock_mode_active": llm_adapter.settings.mock_llm,
                "available_providers": list(llm_adapter.clients.keys()),
                "prompt_templates": list(llm_adapter.prompts.keys())
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage stats retrieval failed: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data(days_back: int = Query(7, ge=1, le=30)):
    """
    Get comprehensive dashboard data for analytics overview
    
    Returns a summary of key metrics, patterns, and insights
    for the specified time period.
    """
    try:
        # Get pattern alerts
        alerts = await pattern_engine.analyze_dispute_patterns(days_back)
        
        # Get LLM usage stats
        llm_stats = llm_adapter.get_usage_stats()
        
        # Summarize alerts by type and severity
        alert_summary = {
            "total_alerts": len(alerts),
            "by_severity": {},
            "by_type": {},
            "high_priority": []
        }
        
        for alert in alerts:
            # Count by severity
            severity = alert.severity.value
            alert_summary["by_severity"][severity] = alert_summary["by_severity"].get(severity, 0) + 1
            
            # Count by type
            pattern_type = alert.pattern_type.value
            alert_summary["by_type"][pattern_type] = alert_summary["by_type"].get(pattern_type, 0) + 1
            
            # Collect high priority alerts
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                alert_summary["high_priority"].append({
                    "title": alert.title,
                    "severity": severity,
                    "confidence": alert.confidence_score
                })
        
        return {
            "period_days": days_back,
            "generated_at": datetime.utcnow(),
            "alerts": alert_summary,
            "llm_usage": {
                "total_cost": llm_stats.get("total_cost", 0.0),
                "total_tokens": llm_stats.get("total_tokens", 0),
                "mock_mode": llm_adapter.settings.mock_llm
            },
            "recommendations": [
                "Review high-priority alerts for immediate action",
                "Monitor merchants with elevated risk scores",
                "Consider implementing automated responses for pattern alerts"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data generation failed: {str(e)}")

@router.get("/health")
async def analytics_health_check():
    """Health check for analytics services"""
    try:
        # Test pattern engine
        test_alerts = await pattern_engine.analyze_dispute_patterns(1)
        pattern_engine_healthy = True
    except Exception:
        pattern_engine_healthy = False
    
    # Test LLM adapter
    try:
        llm_stats = llm_adapter.get_usage_stats()
        llm_adapter_healthy = True
    except Exception:
        llm_adapter_healthy = False
    
    # Test PII redactor
    try:
        test_text = "Test email: test@example.com"
        pii_redactor.detect_pii(test_text)
        pii_redactor_healthy = True
    except Exception:
        pii_redactor_healthy = False
    
    overall_healthy = all([
        pattern_engine_healthy,
        llm_adapter_healthy,
        pii_redactor_healthy
    ])
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "components": {
            "pattern_engine": "healthy" if pattern_engine_healthy else "unhealthy",
            "llm_adapter": "healthy" if llm_adapter_healthy else "unhealthy",
            "pii_redactor": "healthy" if pii_redactor_healthy else "unhealthy"
        },
        "timestamp": datetime.utcnow()
    }