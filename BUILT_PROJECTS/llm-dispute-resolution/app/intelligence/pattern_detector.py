"""
Advanced Pattern Detection Engine

This module provides intelligent pattern detection capabilities for:
- Fraud cluster identification
- Anomaly detection in dispute patterns
- Trend analysis and early warning systems
- Merchant risk scoring
- Customer behavior analysis
"""

import asyncio
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import json

from ..infra.db import get_session
from ..domain.models import DisputeCase, TransactionLedger
from sqlalchemy import select, func, and_, or_
from sqlalchemy.sql import text

class PatternType(Enum):
    """Types of patterns that can be detected"""
    FRAUD_CLUSTER = "fraud_cluster"
    MERCHANT_ANOMALY = "merchant_anomaly"
    CUSTOMER_ANOMALY = "customer_anomaly"
    TIME_ANOMALY = "time_anomaly"
    AMOUNT_ANOMALY = "amount_anomaly"

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PatternAlert:
    """Represents a detected pattern that requires attention"""
    id: str
    pattern_type: PatternType
    severity: AlertSeverity
    title: str
    description: str
    entities_involved: List[str]
    confidence_score: float
    detected_at: datetime
    metadata: Dict[str, Any]

class PatternDetectionEngine:
    """
    Advanced pattern detection engine using statistical analysis
    and machine learning techniques to identify suspicious patterns
    """
    
    def __init__(self):
        self.alert_threshold = {
            PatternType.FRAUD_CLUSTER: 0.8,
            PatternType.MERCHANT_ANOMALY: 0.7,
            PatternType.CUSTOMER_ANOMALY: 0.75,
            PatternType.TIME_ANOMALY: 0.65,
            PatternType.AMOUNT_ANOMALY: 0.7
        }
    
    async def analyze_dispute_patterns(self, days_back: int = 30) -> List[PatternAlert]:
        """
        Analyze recent disputes for suspicious patterns
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            List of pattern alerts
        """
        alerts = []
        
        # Parallel analysis of different pattern types
        tasks = [
            self._detect_fraud_clusters(days_back),
            self._detect_merchant_anomalies(days_back),
            self._detect_customer_anomalies(days_back),
            self._detect_time_anomalies(days_back),
            self._detect_amount_anomalies(days_back)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                alerts.extend(result)
            elif isinstance(result, Exception):
                print(f"Pattern detection error: {result}")
        
        return sorted(alerts, key=lambda x: (x.severity.value, x.confidence_score), reverse=True)
    
    async def _detect_fraud_clusters(self, days_back: int) -> List[PatternAlert]:
        """Detect clusters of fraudulent disputes"""
        alerts = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with get_session() as session:
            # Find fraud disputes by merchant
            stmt = select(
                DisputeCase.merchant_id,
                func.count(DisputeCase.id).label('fraud_count'),
                func.avg(DisputeCase.amount_cents).label('avg_amount')
            ).where(
                and_(
                    DisputeCase.created_at >= cutoff_date,
                    DisputeCase.classification.like('%FRAUD%')
                )
            ).group_by(DisputeCase.merchant_id)
            
            result = await session.execute(stmt)
            merchant_fraud_stats = result.fetchall()
            
            for merchant_id, fraud_count, avg_amount in merchant_fraud_stats:
                if fraud_count >= 5:  # Threshold for cluster detection
                    confidence = min(0.9, 0.6 + (fraud_count - 5) * 0.05)
                    
                    severity = AlertSeverity.HIGH if fraud_count >= 10 else AlertSeverity.MEDIUM
                    
                    alerts.append(PatternAlert(
                        id=f"fraud_cluster_{merchant_id}_{int(time.time())}",
                        pattern_type=PatternType.FRAUD_CLUSTER,
                        severity=severity,
                        title=f"Fraud Cluster Detected - Merchant {merchant_id}",
                        description=f"Detected {fraud_count} fraud disputes for merchant {merchant_id} in the last {days_back} days",
                        entities_involved=[merchant_id],
                        confidence_score=confidence,
                        detected_at=datetime.utcnow(),
                        metadata={
                            "fraud_count": fraud_count,
                            "avg_amount": float(avg_amount or 0),
                            "days_analyzed": days_back
                        }
                    ))
        
        return alerts
    
    async def _detect_merchant_anomalies(self, days_back: int) -> List[PatternAlert]:
        """Detect unusual patterns in merchant behavior"""
        alerts = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with get_session() as session:
            # Calculate dispute rates by merchant
            stmt = text("""
                SELECT 
                    merchant_id,
                    COUNT(*) as total_disputes,
                    COUNT(CASE WHEN classification LIKE '%FRAUD%' THEN 1 END) as fraud_disputes,
                    AVG(amount_cents) as avg_amount,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM dispute_case 
                WHERE created_at >= :cutoff_date 
                GROUP BY merchant_id 
                HAVING COUNT(*) >= 3
            """)
            
            result = await session.execute(stmt, {"cutoff_date": cutoff_date})
            merchant_stats = result.fetchall()
            
            for row in merchant_stats:
                merchant_id = row.merchant_id
                total_disputes = row.total_disputes
                fraud_disputes = row.fraud_disputes
                avg_amount = row.avg_amount
                unique_customers = row.unique_customers
                
                fraud_rate = fraud_disputes / total_disputes if total_disputes > 0 else 0
                
                # Anomaly detection based on fraud rate and customer diversity
                if fraud_rate > 0.4:  # High fraud rate
                    confidence = min(0.95, 0.5 + fraud_rate)
                    severity = AlertSeverity.HIGH if fraud_rate > 0.6 else AlertSeverity.MEDIUM
                    
                    alerts.append(PatternAlert(
                        id=f"merchant_anomaly_{merchant_id}_{int(time.time())}",
                        pattern_type=PatternType.MERCHANT_ANOMALY,
                        severity=severity,
                        title=f"High Fraud Rate - Merchant {merchant_id}",
                        description=f"Merchant {merchant_id} has {fraud_rate:.1%} fraud rate ({fraud_disputes}/{total_disputes} disputes)",
                        entities_involved=[merchant_id],
                        confidence_score=confidence,
                        detected_at=datetime.utcnow(),
                        metadata={
                            "fraud_rate": fraud_rate,
                            "total_disputes": total_disputes,
                            "fraud_disputes": fraud_disputes,
                            "avg_amount": float(avg_amount or 0),
                            "unique_customers": unique_customers
                        }
                    ))
        
        return alerts
    
    async def _detect_customer_anomalies(self, days_back: int) -> List[PatternAlert]:
        """Detect unusual customer dispute patterns"""
        alerts = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with get_session() as session:
            # Find customers with multiple disputes
            stmt = select(
                DisputeCase.customer_id,
                func.count(DisputeCase.id).label('dispute_count'),
                func.count(func.distinct(DisputeCase.merchant_id)).label('merchant_count'),
                func.sum(DisputeCase.amount_cents).label('total_amount')
            ).where(
                DisputeCase.created_at >= cutoff_date
            ).group_by(
                DisputeCase.customer_id
            ).having(
                func.count(DisputeCase.id) >= 3
            )
            
            result = await session.execute(stmt)
            customer_stats = result.fetchall()
            
            for customer_id, dispute_count, merchant_count, total_amount in customer_stats:
                if dispute_count >= 5:  # Multiple disputes threshold
                    # Higher suspicion if disputes span multiple merchants
                    merchant_diversity = merchant_count / dispute_count
                    confidence = 0.6 + (dispute_count - 5) * 0.05 + merchant_diversity * 0.2
                    confidence = min(0.95, confidence)
                    
                    severity = AlertSeverity.HIGH if dispute_count >= 8 else AlertSeverity.MEDIUM
                    
                    alerts.append(PatternAlert(
                        id=f"customer_anomaly_{customer_id}_{int(time.time())}",
                        pattern_type=PatternType.CUSTOMER_ANOMALY,
                        severity=severity,
                        title=f"High Dispute Activity - Customer {customer_id}",
                        description=f"Customer {customer_id} has {dispute_count} disputes across {merchant_count} merchants",
                        entities_involved=[customer_id],
                        confidence_score=confidence,
                        detected_at=datetime.utcnow(),
                        metadata={
                            "dispute_count": dispute_count,
                            "merchant_count": merchant_count,
                            "total_amount": float(total_amount or 0),
                            "merchant_diversity": merchant_diversity
                        }
                    ))
        
        return alerts
    
    async def _detect_time_anomalies(self, days_back: int) -> List[PatternAlert]:
        """Detect unusual temporal patterns in disputes"""
        alerts = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with get_session() as session:
            # Analyze disputes by hour of day
            stmt = text("""
                SELECT 
                    strftime('%H', created_at) as hour,
                    COUNT(*) as dispute_count,
                    COUNT(CASE WHEN classification LIKE '%FRAUD%' THEN 1 END) as fraud_count
                FROM dispute_case 
                WHERE created_at >= :cutoff_date 
                GROUP BY strftime('%H', created_at)
                ORDER BY hour
            """)
            
            result = await session.execute(stmt, {"cutoff_date": cutoff_date})
            hourly_stats = result.fetchall()
            
            if len(hourly_stats) >= 5:  # Need sufficient data
                hours = [int(row.hour) for row in hourly_stats]
                counts = [row.dispute_count for row in hourly_stats]
                
                # Simple anomaly detection using z-score
                mean_count = np.mean(counts)
                std_count = np.std(counts)
                
                for i, (hour, count) in enumerate(zip(hours, counts)):
                    if std_count > 0:
                        z_score = abs(count - mean_count) / std_count
                        
                        if z_score > 2.5:  # Significant deviation
                            confidence = min(0.9, 0.5 + (z_score - 2.5) * 0.1)
                            severity = AlertSeverity.MEDIUM if z_score > 3 else AlertSeverity.LOW
                            
                            alerts.append(PatternAlert(
                                id=f"time_anomaly_hour_{hour}_{int(time.time())}",
                                pattern_type=PatternType.TIME_ANOMALY,
                                severity=severity,
                                title=f"Unusual Activity - Hour {hour:02d}:00",
                                description=f"Detected {count} disputes at hour {hour}, significantly above average ({mean_count:.1f})",
                                entities_involved=[f"hour_{hour}"],
                                confidence_score=confidence,
                                detected_at=datetime.utcnow(),
                                metadata={
                                    "hour": hour,
                                    "dispute_count": count,
                                    "average_count": mean_count,
                                    "z_score": z_score
                                }
                            ))
        
        return alerts
    
    async def _detect_amount_anomalies(self, days_back: int) -> List[PatternAlert]:
        """Detect unusual patterns in dispute amounts"""
        alerts = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with get_session() as session:
            # Analyze amount distributions
            stmt = select(
                DisputeCase.amount_cents,
                DisputeCase.merchant_id,
                DisputeCase.customer_id
            ).where(
                DisputeCase.created_at >= cutoff_date
            )
            
            result = await session.execute(stmt)
            amounts_data = result.fetchall()
            
            if len(amounts_data) >= 10:  # Need sufficient data
                amounts = [row.amount_cents for row in amounts_data]
                
                # Detect suspiciously round amounts (potential fraud indicator)
                round_amounts = [amt for amt in amounts if amt % 10000 == 0]  # Round to nearest $100
                round_percentage = len(round_amounts) / len(amounts)
                
                if round_percentage > 0.3:  # More than 30% round amounts
                    confidence = min(0.8, 0.4 + round_percentage)
                    severity = AlertSeverity.MEDIUM if round_percentage > 0.5 else AlertSeverity.LOW
                    
                    alerts.append(PatternAlert(
                        id=f"amount_anomaly_round_{int(time.time())}",
                        pattern_type=PatternType.AMOUNT_ANOMALY,
                        severity=severity,
                        title="Suspicious Round Amount Pattern",
                        description=f"{round_percentage:.1%} of disputes have suspiciously round amounts",
                        entities_involved=["amount_pattern"],
                        confidence_score=confidence,
                        detected_at=datetime.utcnow(),
                        metadata={
                            "round_percentage": round_percentage,
                            "total_disputes": len(amounts),
                            "round_disputes": len(round_amounts),
                            "common_amounts": list(set(round_amounts))[:10]
                        }
                    ))
        
        return alerts
    
    async def get_merchant_risk_score(self, merchant_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Calculate comprehensive risk score for a merchant"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with get_session() as session:
            # Get merchant dispute statistics
            stmt = text("""
                SELECT 
                    COUNT(*) as total_disputes,
                    COUNT(CASE WHEN classification LIKE '%FRAUD%' THEN 1 END) as fraud_disputes,
                    AVG(amount_cents) as avg_amount,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    MIN(created_at) as first_dispute,
                    MAX(created_at) as last_dispute
                FROM dispute_case 
                WHERE merchant_id = :merchant_id AND created_at >= :cutoff_date
            """)
            
            result = await session.execute(stmt, {
                "merchant_id": merchant_id,
                "cutoff_date": cutoff_date
            })
            
            stats = result.fetchone()
            
            if not stats or stats.total_disputes == 0:
                return {
                    "merchant_id": merchant_id,
                    "risk_score": 0.0,
                    "risk_level": "UNKNOWN",
                    "factors": {"reason": "No recent dispute data"}
                }
            
            # Calculate risk factors
            fraud_rate = stats.fraud_disputes / stats.total_disputes
            dispute_frequency = stats.total_disputes / days_back  # Disputes per day
            
            # Risk scoring algorithm
            risk_score = 0.0
            risk_factors = {}
            
            # Fraud rate contribution (0-40 points)
            fraud_score = min(40, fraud_rate * 100)
            risk_score += fraud_score
            risk_factors["fraud_rate"] = {"score": fraud_score, "value": fraud_rate}
            
            # Dispute frequency contribution (0-30 points)
            freq_score = min(30, dispute_frequency * 10)
            risk_score += freq_score
            risk_factors["dispute_frequency"] = {"score": freq_score, "value": dispute_frequency}
            
            # Customer diversity (lack of diversity = higher risk) (0-20 points)
            diversity_ratio = stats.unique_customers / stats.total_disputes
            diversity_score = max(0, 20 - (diversity_ratio * 20))
            risk_score += diversity_score
            risk_factors["customer_diversity"] = {"score": diversity_score, "value": diversity_ratio}
            
            # Normalize to 0-100 scale
            risk_score = min(100, risk_score)
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = "HIGH"
            elif risk_score >= 40:
                risk_level = "MEDIUM"
            elif risk_score >= 20:
                risk_level = "LOW"
            else:
                risk_level = "MINIMAL"
            
            return {
                "merchant_id": merchant_id,
                "risk_score": round(risk_score, 2),
                "risk_level": risk_level,
                "factors": risk_factors,
                "stats": {
                    "total_disputes": stats.total_disputes,
                    "fraud_disputes": stats.fraud_disputes,
                    "fraud_rate": round(fraud_rate, 3),
                    "avg_amount": float(stats.avg_amount or 0),
                    "unique_customers": stats.unique_customers,
                    "dispute_frequency": round(dispute_frequency, 2)
                }
            }

# Global pattern detection engine instance
pattern_engine = PatternDetectionEngine()