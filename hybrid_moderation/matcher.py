
import re
import difflib
from typing import List, Tuple

from .config import NEUTRAL_IDENTITY_TERMS

class KeywordMatcher:
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenizer that removes punctuation and lowercases."""
        # Keep alphanumeric and spaces, remove others
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().split()

    def calculate_match_confidence(self, text: str, keywords: List[str]) -> Tuple[float, List[str]]:
        """
        Calculates confidence based on keyword presence.
        Returns (confidence_score, matched_keywords).
        """
        if not keywords:
            return 0.0, []

        tokens = self.tokenize(text)
        text_lower = text.lower()
        
        matches = []
        match_count = 0
        
        # Check for phrase matches first (multi-word keywords)
        for kw in keywords:
            if not kw: continue

            if kw.lower() in NEUTRAL_IDENTITY_TERMS:
                continue
            
            # Direct containment
            if kw in text_lower:
                matches.append(kw)
                match_count += 3 # Phrases weight more
                continue

            # Fuzzy Match for single words
            # Only if keyword is single word
            if ' ' not in kw:
                for token in tokens:
                    ratio = difflib.SequenceMatcher(None, kw, token).ratio()
                    if ratio > 0.85: # Threshold for typo tolerance
                        matches.append(kw)
                        match_count += 1
                        break
        
        if not matches:
            return 0.0, []

        # Simple density/frequency scoring
        # Cap at 1.0
        # If we have at least 1 strong match (phrase) or 3 word matches, high confidence
        score = min(1.0, match_count * 0.35) 
        
        return score, list(set(matches))
