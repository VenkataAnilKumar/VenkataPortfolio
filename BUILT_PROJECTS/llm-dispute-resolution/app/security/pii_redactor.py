"""
PII Redaction Module for Data Privacy and Security

This module provides comprehensive PII detection and redaction capabilities
to ensure compliance with privacy regulations and prevent sensitive data
from being sent to external LLM providers.
"""

import re
from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass

class PIIType(Enum):
    """Types of PII that can be detected and redacted"""
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    ACCOUNT_NUMBER = "account_number"
    ROUTING_NUMBER = "routing_number"

@dataclass
class PIIMatch:
    """Represents a detected PII instance"""
    pii_type: PIIType
    original_text: str
    start_pos: int
    end_pos: int
    confidence: float

class PIIRedactor:
    """
    Advanced PII detection and redaction system
    
    Features:
    - Multiple PII type detection (SSN, email, phone, credit cards, etc.)
    - Configurable redaction patterns
    - Audit trail of redactions
    - Context-aware replacement
    """
    
    def __init__(self):
        self.patterns = self._init_patterns()
        self.redaction_map = {}  # For reversal if needed
        
    def _init_patterns(self) -> Dict[PIIType, re.Pattern]:
        """Initialize regex patterns for PII detection"""
        return {
            PIIType.SSN: re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            PIIType.PHONE: re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            PIIType.CREDIT_CARD: re.compile(r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6011)[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            PIIType.IP_ADDRESS: re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'),
            PIIType.ACCOUNT_NUMBER: re.compile(r'\b(?:account|acct)[\s#:]*(\d{8,16})\b', re.IGNORECASE),
            PIIType.ROUTING_NUMBER: re.compile(r'\b(?:routing|rtn)[\s#:]*(\d{9})\b', re.IGNORECASE),
        }
    
    def detect_pii(self, text: str) -> List[PIIMatch]:
        """
        Detect all PII instances in the given text
        
        Args:
            text: Input text to scan for PII
            
        Returns:
            List of PIIMatch objects representing detected PII
        """
        matches = []
        
        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                confidence = self._calculate_confidence(pii_type, match.group())
                if confidence > 0.7:  # Threshold for PII detection
                    matches.append(PIIMatch(
                        pii_type=pii_type,
                        original_text=match.group(),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence
                    ))
        
        return sorted(matches, key=lambda x: x.start_pos)
    
    def _calculate_confidence(self, pii_type: PIIType, text: str) -> float:
        """Calculate confidence score for PII detection"""
        # Basic confidence calculation - can be enhanced with ML models
        base_confidence = 0.8
        
        if pii_type == PIIType.EMAIL and '@' in text and '.' in text:
            return 0.95
        elif pii_type == PIIType.SSN and len(text.replace('-', '')) == 9:
            return 0.9
        elif pii_type == PIIType.PHONE and len(text.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')) >= 10:
            return 0.85
        elif pii_type == PIIType.CREDIT_CARD:
            # Basic Luhn algorithm check could be added here
            return 0.8
            
        return base_confidence
    
    def redact_text(self, text: str, redaction_char: str = "*") -> Tuple[str, List[PIIMatch]]:
        """
        Redact PII from text while preserving structure
        
        Args:
            text: Input text to redact
            redaction_char: Character to use for redaction
            
        Returns:
            Tuple of (redacted_text, detected_pii_list)
        """
        pii_matches = self.detect_pii(text)
        redacted_text = text
        
        # Process matches in reverse order to preserve positions
        for match in reversed(pii_matches):
            redacted_value = self._generate_redaction(match, redaction_char)
            redacted_text = (
                redacted_text[:match.start_pos] + 
                redacted_value + 
                redacted_text[match.end_pos:]
            )
            
        return redacted_text, pii_matches
    
    def _generate_redaction(self, match: PIIMatch, redaction_char: str) -> str:
        """Generate context-appropriate redaction"""
        if match.pii_type == PIIType.EMAIL:
            # Preserve domain for context: "user@domain.com" -> "****@domain.com"
            parts = match.original_text.split('@')
            if len(parts) == 2:
                return redaction_char * 4 + '@' + parts[1]
        elif match.pii_type == PIIType.PHONE:
            # Preserve format: "(555) 123-4567" -> "(***) ***-****"
            return re.sub(r'\d', redaction_char, match.original_text)
        elif match.pii_type == PIIType.CREDIT_CARD:
            # Show last 4 digits: "1234 5678 9012 3456" -> "**** **** **** 3456"
            digits_only = re.sub(r'\D', '', match.original_text)
            if len(digits_only) >= 4:
                last_four = digits_only[-4:]
                redacted_part = redaction_char * (len(digits_only) - 4)
                # Preserve original formatting
                result = match.original_text
                for i, char in enumerate(match.original_text):
                    if char.isdigit():
                        if i < len(match.original_text) - 4:
                            result = result[:i] + redaction_char + result[i+1:]
                return result
        
        # Default: replace all with redaction character
        return redaction_char * len(match.original_text)
    
    def get_redaction_summary(self, pii_matches: List[PIIMatch]) -> Dict[str, int]:
        """Generate summary of redacted PII types"""
        summary = {}
        for match in pii_matches:
            pii_type = match.pii_type.value
            summary[pii_type] = summary.get(pii_type, 0) + 1
        return summary

# Global redactor instance
pii_redactor = PIIRedactor()

def sanitize_for_llm(text: str) -> Tuple[str, Dict]:
    """
    Sanitize text before sending to LLM by removing PII
    
    Args:
        text: Input text that may contain PII
        
    Returns:
        Tuple of (sanitized_text, redaction_metadata)
    """
    redacted_text, pii_matches = pii_redactor.redact_text(text)
    
    metadata = {
        "pii_detected": len(pii_matches) > 0,
        "pii_summary": pii_redactor.get_redaction_summary(pii_matches),
        "redaction_count": len(pii_matches)
    }
    
    return redacted_text, metadata