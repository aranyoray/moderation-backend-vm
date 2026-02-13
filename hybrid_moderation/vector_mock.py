
import random
from typing import Dict, List, Tuple
from .models import VectorAnalysisResult

class VectorSearchClient:
    """
    Mock implementation of the Vector Search System.
    In a real implementation, this would connect to an Embeddings API and Vector DB.
    """
    def __init__(self):
        pass

    def semantic_analyze(self, text: str, categories: List[str]) -> VectorAnalysisResult:
        """
        Simulates semantic analysis.
        Returns a high confidence match if 'violence' or 'explicit' words are found for demo purposes.
        Otherwise checks for exact string matches in mock "embeddings".
        """
        text_lower = text.lower()
        
        # Simple heuristic for mock purposes
        if "violent" in text_lower or "kill" in text_lower or "blood" in text_lower:
             return VectorAnalysisResult(
                semantic_category="Violence & Disturbing Content",
                confidence=0.95,
                embedding_similarity=0.92
            )
        elif "sex" in text_lower or "nude" in text_lower:
             return VectorAnalysisResult(
                semantic_category="Explicit & Body-Related Content",
                confidence=0.98,
                embedding_similarity=0.96
            )
        elif "gamble" in text_lower or "bet" in text_lower:
            return VectorAnalysisResult(
                semantic_category="Substances & Addictive Behavior",
                confidence=0.90,
                embedding_similarity=0.88
            )

        # Default low confidence result
        return VectorAnalysisResult(
            semantic_category="General",
            confidence=0.2,
            embedding_similarity=0.15
        )
