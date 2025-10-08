"""
PII Detection and Redaction Module.
Handles sensitive data detection and secure redaction in dispute narratives.
"""
from typing import Dict, List, Optional, Tuple
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import spacy
from app.core.config import get_settings

settings = get_settings()

# Initialize NLP and Presidio engines
nlp_engine = NlpEngine(nlp_configuration={"lang_code": "en"})
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
anonymizer = AnonymizerEngine()

# Custom PII patterns and rules
CUSTOM_PII_PATTERNS = {
    "CARD_NUMBER": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "SSN": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
    "PHONE_US": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
}

class PIIHandler:
    """Handles PII detection and redaction in text."""
    
    def __init__(self):
        """Initialize PII handler with configuration."""
        self.confidence_threshold = settings.pii_confidence_threshold
        self.enabled = settings.enable_pii_redaction
    
    async def analyze_text(self, text: str) -> Dict[str, List[Dict]]:
        """
        Analyze text for PII entities.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with PII types and their occurrences
        """
        if not self.enabled or not text:
            return {"pii_found": [], "stats": {"total_pii": 0}}
            
        # Get PII analysis results
        results = analyzer.analyze(
            text=text,
            language="en",
            score_threshold=self.confidence_threshold
        )
        
        # Group findings by PII type
        pii_findings = {}
        for result in results:
            pii_type = result.entity_type
            if pii_type not in pii_findings:
                pii_findings[pii_type] = []
            
            pii_findings[pii_type].append({
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start:result.end]
            })
            
        return {
            "pii_found": [
                {
                    "type": pii_type,
                    "count": len(findings),
                    "samples": findings[:2]  # Only return first 2 examples
                }
                for pii_type, findings in pii_findings.items()
            ],
            "stats": {
                "total_pii": sum(len(f) for f in pii_findings.values())
            }
        }

    async def redact_text(
        self, 
        text: str,
        mask_type: str = "hash",
        preserve_format: bool = True
    ) -> Tuple[str, Dict]:
        """
        Redact PII entities from text.
        
        Args:
            text: Input text to redact
            mask_type: Type of masking ('hash', 'asterisk', 'encrypted')
            preserve_format: Whether to preserve the format of redacted values
            
        Returns:
            Tuple of (redacted_text, redaction_stats)
        """
        if not self.enabled or not text:
            return text, {"total_redactions": 0}
            
        # Analyze text for PII
        results = analyzer.analyze(
            text=text,
            language="en",
            score_threshold=self.confidence_threshold
        )
        
        # Configure anonymizer
        operator_config = {
            "type": {
                "operator": mask_type,
                "preserve_format": preserve_format
            }
        }
        
        # Perform redaction
        anon_results = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operator_config
        )
        
        # Count redactions by type
        redaction_counts = {}
        for result in results:
            pii_type = result.entity_type
            redaction_counts[pii_type] = redaction_counts.get(pii_type, 0) + 1
            
        stats = {
            "total_redactions": len(results),
            "redactions_by_type": redaction_counts
        }
        
        return anon_results.text, stats

    async def validate_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate text for potential sensitive data leaks.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return True, None
            
        # Check for high-risk PII patterns
        results = analyzer.analyze(
            text=text,
            language="en",
            score_threshold=0.9  # Higher threshold for validation
        )
        
        high_risk_types = {"CREDIT_CARD", "SSN", "PASSPORT_NUMBER"}
        found_high_risk = [r for r in results if r.entity_type in high_risk_types]
        
        if found_high_risk:
            types_found = {r.entity_type for r in found_high_risk}
            return False, f"Found sensitive data: {', '.join(types_found)}"
            
        return True, None