import re
from typing import List

class ContextValidator:
    """
    Analyzes the context around a keyword to determine if it's used safely 
    (e.g., in educational, medical, or news contexts).
    """

    SAFE_CONTEXT_KEYWORDS = {
        'education': [
            'education', 'learn', 'study', 'university', 'college', 'professor', 
            'biology', 'science', 'research', 'academic', 'textbook', 'lesson',
            'course', 'history', 'health class', 'awareness', 'prevention'
        ],
        'medical': [
            'medical', 'doctor', 'hospital', 'treatment', 'symptom', 'diagnosis',
            'health', 'anatomy', 'clinical', 'patient', 'recovery', 'therapy',
            'wellness', 'medicine', 'condition'
        ],
        'news': [
            'news', 'report', 'article', 'breaking', 'journalist', 'media',
            'coverage', 'politics', 'debate', 'discussion', 'opinion'
        ],
        'general_safe': [
            'consent', 'safe', 'responsibility', 'information', 'guide',
            'help', 'support', 'hotline', 'resource'
        ]
    }

    # Compile logic into a single list for broad checking, or keep separate if we want detailed reasoning
    ALL_SAFE_TERMS = set(
        term for category in SAFE_CONTEXT_KEYWORDS.values() for term in category
    )

    def __init__(self, context_window: int = 150):
        self.context_window = context_window

    def is_safe_context(self, text: str, keyword: str) -> bool:
        """
        Checks if the keyword appears in a safe context within the text.
        """
        if not text or not keyword:
            return False

        # Find all occurrences of the keyword
        # Note: This simple regex match might mismatch if fuzzy matching was used originally,
        # but for context validation we need to find the anchors.
        
        # Escape keyword for regex
        escaped_kw = re.escape(keyword)
        # Match whole word to avoid identifying 'class' inside 'classification' if that's not desired,
        # but keywords often need flexibility. Let's use boundary if possible.
        pattern = re.compile(rf'{escaped_kw}', re.IGNORECASE)
        
        matches = list(pattern.finditer(text))
        
        if not matches:
            # Keyword not found exactly (maybe fuzzy matched). 
            # Fallback: Check if the WHOLE text is overwhelmingly safe?
            # For now, just return False (not safe override).
            return False

        # Check ANY occurrence for safe context. 
        # Strategy: If ANY occurrence is unsafe, does it poison the whole? 
        # Or if ANY occurrence is safe, is it safe?
        # Usually moderation is "Any Unsafe = Flag". 
        # But here we want to see if the usage is educational.
        # If the text is "Sex education is good but look at this porn", it's UNSAFE.
        # If the text is "Sex education is important", it's SAFE.
        
        # We need to ensure ALL occurrences are in safe context, or that the unsafe usage is absent.
        # Let's count "Safe Contexts" vs "Matches".
        
        safe_count = 0
        total_matches = len(matches)

        for match in matches:
            start_idx = max(0, match.start() - self.context_window)
            end_idx = min(len(text), match.end() + self.context_window)
            
            context_snippet = text[start_idx:end_idx].lower()
            
            # Check for safe keywords in this snippet
            if self._contains_safe_terms(context_snippet):
                safe_count += 1
        
        # If all matches are in safe context, or we have a high ratio?
        # Let's say if > 50% are safe, or if it's short text and it's safe.
        # User said "if the context justifies... take it".
        
        if total_matches > 0 and safe_count == total_matches:
            return True
            
        return False

    def _contains_safe_terms(self, snippet: str) -> bool:
        tokens = set(re.findall(r'\w+', snippet))
        # Check intersection
        common = tokens.intersection(self.ALL_SAFE_TERMS)
        return len(common) > 0

    def get_context_snippet(self, text: str, keyword: str) -> str:
        escaped_kw = re.escape(keyword)
        match = re.search(rf'{escaped_kw}', text, re.IGNORECASE)
        if match:
             start_idx = max(0, match.start() - 50)
             end_idx = min(len(text), match.end() + 50)
             return text[start_idx:end_idx].replace('\n', ' ')
        return ""
