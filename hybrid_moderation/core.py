
import time
import datetime
import sys
from typing import List, Optional
from .loader import CSVLoader
from .models import ModerationResult, CSVAnalysisResult, VectorAnalysisResult, FinalDecision
from .vector_mock import VectorSearchClient
from .matcher import KeywordMatcher
from .context import ContextValidator
from .config import (
    CSV_FILE_PATH, CSV_WEIGHT, VECTOR_WEIGHT,
    PRIMARY_CATEGORY_CONFIDENCE_THRESHOLD
)

class ContentModerationSystem:
    def __init__(self, csv_path: str = CSV_FILE_PATH):
        self.loader = CSVLoader(csv_path)
        self.matcher = KeywordMatcher()
        self.vector_client = VectorSearchClient()
        self.context_validator = ContextValidator()
        self.categories = []

    def initialize(self):
        """Loads data and prepares the system."""
        self.categories = self.loader.load_data()

    def analyze(self, content_id: str, text: str, age_group: str = '13-16') -> ModerationResult:
        print(f"\n[HybridMod] 🚀 Starting analysis for Content ID: {content_id} | Age Group: {age_group}", file=sys.stderr)
        start_time = time.time()
        
        # 1. CSV Processing & Confidence-Based Cascading Logic
        print("[HybridMod] Step 1: Running CSV Keyword Matching...", file=sys.stderr)
        best_csv_result = CSVAnalysisResult()
        best_category_obj = None

        # Iterate all categories to find best match
        # In a real system with huge CSV, you'd use an inverted index or Aho-Corasick
        # Iterate all categories to find best match
        # In a real system with huge CSV, you'd use an inverted index or Aho-Corasick
        for cat in self.categories:
            # Stage 1: Category Match
            cat_score, cat_matches = self.matcher.calculate_match_confidence(text, cat.category_keywords)
            
            # --- CONTEXT AWARENESS CHECK (Category) ---
            if cat_score > 0.0:
                 # Check if this primary match is in a safe context
                is_safe = False
                for kw in cat_matches:
                    if self.context_validator.is_safe_context(text, kw):
                        print(f"[HybridMod]   🛡️ Safe Context Detected for '{kw}' in {cat.category}. Downgrading score.", file=sys.stderr)
                        is_safe = True
                        break
                
                if is_safe:
                    cat_score = cat_score * 0.1 # Heavily penalize the score
                    print(f"[HybridMod]   -> Adjusted Score (Safe Context): {cat_score:.2f}", file=sys.stderr)
                else:
                    print(f"[HybridMod]   -> Candidate: {cat.category} | Keyword Match Score: {cat_score:.2f}", file=sys.stderr)

            # Stage 2: Subcategory Match (Check ALWAYS, not just if cat_score > best)
            sub_score, sub_matches = self.matcher.calculate_match_confidence(text, cat.subcategory_keywords)
            
            # --- CONTEXT AWARENESS CHECK (Subcategory) ---
            if sub_score > 0.0:
                is_sub_safe = False
                for kw in sub_matches:
                        if self.context_validator.is_safe_context(text, kw):
                            is_sub_safe = True
                
                if is_sub_safe:
                    # Only penalize if the category itself is NOT educational/medical
                    # If the category IS educational, we should actually Keep the score high or even Boost it.
                    is_compatible_context = any(term in cat.subcategory.lower() for term in ['education', 'medical', 'health', 'recovery', 'news', 'study'])
                    
                    if is_compatible_context:
                        # Context aligns with category (e.g. sex ed in ed context)
                        # Keep score as is (or potential boost?)
                        print(f"[HybridMod]      -> Subcategory Safe Context aligns with category '{cat.subcategory}'. Keeping score high.", file=sys.stderr)
                    else:
                        sub_score = sub_score * 0.1
                        print(f"[HybridMod]      -> Subcategory Safe Context for {cat.subcategory}. Adjusted Sub-score: {sub_score:.2f}", file=sys.stderr)
                else:
                    print(f"[HybridMod]      -> Subcategory Check: {cat.subcategory} | Sub-score: {sub_score:.2f}", file=sys.stderr)
            
            # Combined confidence calculation
            combined_conf = max(cat_score, sub_score)
            
            matched_kw = []
            if cat_score > 0: matched_kw.extend(cat_matches)
            if sub_score > 0: matched_kw.extend(sub_matches)

            # Update best result if this category is better
            if combined_conf > best_csv_result.confidence:
                print(f"[HybridMod]      -> 🌟 New Best Match: {cat.category} - {cat.subcategory} ({combined_conf:.2f})", file=sys.stderr)
                best_csv_result = CSVAnalysisResult(
                    primary_category=cat.category,
                    subcategory=cat.subcategory,
                    confidence=combined_conf,
                    matched_keywords=list(set(matched_kw)),
                    age_restriction=self._get_age_action(cat.age_rules, age_group)
                )
                best_category_obj = cat

        if best_csv_result.primary_category:
             print(f"[HybridMod] ✅ CSV Analysis Complete. Top Category: {best_csv_result.primary_category} ({best_csv_result.confidence:.2f})", file=sys.stderr)
             print(f"[HybridMod]    Matched Keywords: {best_csv_result.matched_keywords}", file=sys.stderr)
        else:
             print("[HybridMod] ℹ️ CSV Analysis: No significant keyword matches found.", file=sys.stderr)

        # 2. Vector Semantic Validation
        print("[HybridMod] Step 2: Running Vector Semantic Analysis...", file=sys.stderr)
        vector_result = self.vector_client.semantic_analyze(
            text, 
            [c.category for c in self.categories] # Pass distinct categories
        )
        print(f"[HybridMod]    Vector Semantic Category: {vector_result.semantic_category}", file=sys.stderr)
        print(f"[HybridMod]    Vector Confidence: {vector_result.confidence:.2f}", file=sys.stderr)

        # 3. Scoring Algorithm
        print("[HybridMod] Step 3: Calculating Weighted Hybrid Score...", file=sys.stderr)
        final_score = (best_csv_result.confidence * CSV_WEIGHT) + (vector_result.confidence * VECTOR_WEIGHT)
        print(f"[HybridMod]    Calculation: ({best_csv_result.confidence:.2f} * {CSV_WEIGHT}) + ({vector_result.confidence:.2f} * {VECTOR_WEIGHT}) = {final_score:.4f}", file=sys.stderr)

        # 4. Decision Logic
        print("[HybridMod] Step 4: Decision Engine & Age Rules...", file=sys.stderr)
        decision = "PASS"
        action = "Allow with monitoring"
        reasoning = "Content appears safe."

        # Age enforcement override
        print(f"[HybridMod]    Checking Age Rule for group '{age_group}': {best_csv_result.age_restriction}", file=sys.stderr)
        
        # Only apply hard blocking if we have sufficient confidence in the CSV match
        if best_csv_result.age_restriction == "Block" and best_csv_result.confidence > 0.4:
            print(f"[HybridMod] ⛔ AGE RESTRICTION APPLIED: Force-blocking content.", file=sys.stderr)
            decision = "FLAG"
            action = "Blocked by Age Rule"
            reasoning = f"Content blocked for age group {age_group}."
            final_score = 1.0 # Force max score for blocking
        elif final_score >= 0.9:
            decision = "FLAG"
            action = "Block/Review Required"
            reasoning = "High confidence of inappropriate content."
        elif final_score >= 0.7:
            decision = "REVIEW_QUEUE"
            action = "Manual verification needed"
            reasoning = "Moderate confidence, requires review."
        
        print(f"[HybridMod] 🏁 FINAL DECISION: {decision} | Action: {action}", file=sys.stderr)
        
        end_time = time.time()
        
        return ModerationResult(
            content_id=content_id,
            csv_analysis=best_csv_result,
            vector_analysis=vector_result,
            final_decision=FinalDecision(
                weighted_score=round(final_score, 4),
                decision=decision,
                action_required=action,
                reasoning=reasoning
            ),
            metadata={
                "processing_time_ms": int((end_time - start_time) * 1000),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    def _get_age_action(self, rules, age_group):
        if age_group == '<10': return rules.rules_below_10
        if age_group == '10-13': return rules.rules_10_13
        if age_group == '13-16': return rules.rules_13_16
        if age_group == '16+': return rules.rules_16_18 # Maps 16-18 to 16+
        return "Gate" # Default safe
