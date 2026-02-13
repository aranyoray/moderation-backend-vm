from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class AgeRestrictionRules:
    rules_below_10: str
    rules_10_13: str
    rules_13_16: str
    rules_16_18: str

@dataclass
class ModerationCategory:
    category: str
    subcategory: str
    category_keywords: List[str]
    subcategory_keywords: List[str]
    age_rules: AgeRestrictionRules
    # Additional metadata can be added here
    
@dataclass
class CSVAnalysisResult:
    primary_category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence: float = 0.0
    matched_keywords: List[str] = field(default_factory=list)
    age_restriction: Optional[str] = None

@dataclass
class VectorAnalysisResult:
    semantic_category: Optional[str] = None
    confidence: float = 0.0
    embedding_similarity: float = 0.0

@dataclass
class FinalDecision:
    weighted_score: float
    decision: str  # FLAG | REVIEW_QUEUE | PASS
    action_required: str
    reasoning: str

@dataclass
class ModerationResult:
    content_id: str
    csv_analysis: CSVAnalysisResult
    vector_analysis: VectorAnalysisResult
    final_decision: FinalDecision
    metadata: Dict[str, Any]
