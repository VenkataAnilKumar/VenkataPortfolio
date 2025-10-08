"""
Analytics Engine Module.
Handles pattern detection, risk scoring, and business intelligence.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from app.core.config import get_settings

settings = get_settings()

class PatternDetector:
    """Detects fraud patterns and anomalies in dispute data."""
    
    def __init__(self):
        """Initialize pattern detector."""
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.lookback_days = settings.pattern_detection_window_days
        
    async def detect_patterns(
        self,
        disputes: List[Dict],
        merchant_id: Optional[str] = None
    ) -> Dict:
        """
        Detect patterns in dispute data.
        
        Args:
            disputes: List of dispute records
            merchant_id: Optional merchant ID to filter by
            
        Returns:
            Dictionary with detected patterns
        """
        if not disputes:
            return {"patterns": [], "stats": {"total_patterns": 0}}
            
        # Convert to dataframe
        df = pd.DataFrame(disputes)
        
        if merchant_id:
            df = df[df["merchant_id"] == merchant_id]
            
        patterns = []
        
        # Time-based patterns
        time_patterns = self._detect_time_patterns(df)
        patterns.extend(time_patterns)
        
        # Amount patterns
        amount_patterns = self._detect_amount_patterns(df)
        patterns.extend(amount_patterns)
        
        # Customer patterns
        customer_patterns = self._detect_customer_patterns(df)
        patterns.extend(customer_patterns)
        
        return {
            "patterns": patterns,
            "stats": {
                "total_patterns": len(patterns),
                "by_severity": self._count_by_severity(patterns)
            }
        }
        
    def _detect_time_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect time-based patterns."""
        patterns = []
        
        # Detect unusual time concentrations
        df["hour"] = pd.to_datetime(df["created_at"]).dt.hour
        hourly_counts = df["hour"].value_counts()
        
        threshold = hourly_counts.mean() + 2 * hourly_counts.std()
        suspicious_hours = hourly_counts[hourly_counts > threshold]
        
        if not suspicious_hours.empty:
            patterns.append({
                "type": "TIME_CONCENTRATION",
                "severity": "MEDIUM",
                "description": f"Unusual dispute concentration in hours: {suspicious_hours.index.tolist()}",
                "confidence": 0.8
            })
            
        return patterns
        
    def _detect_amount_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect amount-based patterns."""
        patterns = []
        
        # Train isolation forest
        X = df[["amount"]].values
        outliers = self.isolation_forest.fit_predict(X)
        
        # Find outlier amounts
        outlier_amounts = df[outliers == -1]["amount"]
        if not outlier_amounts.empty:
            patterns.append({
                "type": "AMOUNT_ANOMALY",
                "severity": "HIGH",
                "description": f"Detected {len(outlier_amounts)} unusual amount patterns",
                "confidence": 0.9
            })
            
        # Check for repeated amounts
        value_counts = df["amount"].value_counts()
        suspicious_amounts = value_counts[value_counts > 3]
        
        if not suspicious_amounts.empty:
            patterns.append({
                "type": "REPEATED_AMOUNT",
                "severity": "MEDIUM",
                "description": f"Found repeated amounts: {suspicious_amounts.index.tolist()[:3]}",
                "confidence": 0.85
            })
            
        return patterns
        
    def _detect_customer_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect customer behavior patterns."""
        patterns = []
        
        # Check for multiple disputes per customer
        customer_counts = df["customer_id"].value_counts()
        suspicious_customers = customer_counts[customer_counts > 3]
        
        if not suspicious_customers.empty:
            patterns.append({
                "type": "CUSTOMER_FREQUENCY",
                "severity": "HIGH",
                "description": f"Customers with high dispute frequency: {len(suspicious_customers)}",
                "confidence": 0.9
            })
            
        return patterns
        
    def _count_by_severity(self, patterns: List[Dict]) -> Dict[str, int]:
        """Count patterns by severity level."""
        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for pattern in patterns:
            counts[pattern["severity"]] += 1
        return counts


class RiskScorer:
    """Calculates risk scores for merchants and customers."""
    
    def __init__(self):
        """Initialize risk scorer."""
        self.risk_threshold = settings.risk_score_threshold
        
    async def calculate_merchant_risk(
        self,
        merchant_id: str,
        disputes: List[Dict]
    ) -> Dict:
        """
        Calculate risk score for a merchant.
        
        Args:
            merchant_id: Merchant identifier
            disputes: List of disputes for merchant
            
        Returns:
            Dictionary with risk analysis
        """
        if not disputes:
            return {"risk_score": 0.0, "factors": []}
            
        risk_factors = []
        risk_score = 0.0
        
        # Calculate dispute rate
        total_disputes = len(disputes)
        recent_disputes = len([
            d for d in disputes
            if (datetime.now() - datetime.fromisoformat(d["created_at"])).days <= 30
        ])
        
        monthly_rate = recent_disputes / 30.0
        if monthly_rate > 10:
            risk_factors.append({
                "type": "HIGH_DISPUTE_RATE",
                "description": f"High monthly dispute rate: {monthly_rate:.1f}",
                "impact": 0.3
            })
            risk_score += 0.3
            
        # Check resolution rate
        resolved = len([d for d in disputes if d["status"] == "RESOLVED"])
        resolution_rate = resolved / total_disputes
        
        if resolution_rate < 0.5:
            risk_factors.append({
                "type": "LOW_RESOLUTION_RATE",
                "description": f"Low dispute resolution rate: {resolution_rate:.1%}",
                "impact": 0.25
            })
            risk_score += 0.25
            
        # Analyze dispute types
        types = pd.Series([d["type"] for d in disputes])
        fraud_ratio = len(types[types.str.startswith("FRAUD")]) / total_disputes
        
        if fraud_ratio > 0.3:
            risk_factors.append({
                "type": "HIGH_FRAUD_RATIO",
                "description": f"High fraud dispute ratio: {fraud_ratio:.1%}",
                "impact": 0.35
            })
            risk_score += 0.35
            
        return {
            "merchant_id": merchant_id,
            "risk_score": min(risk_score, 1.0),
            "factors": risk_factors,
            "stats": {
                "total_disputes": total_disputes,
                "monthly_rate": monthly_rate,
                "resolution_rate": resolution_rate,
                "fraud_ratio": fraud_ratio
            }
        }


class AnalyticsEngine:
    """Main analytics engine combining pattern detection and risk scoring."""
    
    def __init__(self):
        """Initialize analytics engine."""
        self.pattern_detector = PatternDetector()
        self.risk_scorer = RiskScorer()
        
    async def analyze_merchant(
        self,
        merchant_id: str,
        disputes: List[Dict]
    ) -> Dict:
        """
        Perform comprehensive merchant analysis.
        
        Args:
            merchant_id: Merchant identifier
            disputes: List of disputes
            
        Returns:
            Dictionary with complete analysis
        """
        # Run parallel analysis
        patterns = await self.pattern_detector.detect_patterns(
            disputes,
            merchant_id
        )
        
        risk = await self.risk_scorer.calculate_merchant_risk(
            merchant_id,
            disputes
        )
        
        # Combine results
        return {
            "merchant_id": merchant_id,
            "summary": {
                "risk_score": risk["risk_score"],
                "total_patterns": patterns["stats"]["total_patterns"],
                "alert_level": "HIGH" if risk["risk_score"] > 0.8 else "MEDIUM" if risk["risk_score"] > 0.5 else "LOW"
            },
            "patterns": patterns["patterns"],
            "risk_analysis": risk,
            "timestamp": datetime.now().isoformat()
        }