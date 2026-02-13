
import csv
import logging
import sys
from typing import List
from .models import ModerationCategory, AgeRestrictionRules

logger = logging.getLogger(__name__)

class CSVLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.categories: List[ModerationCategory] = []

    def load_data(self) -> List[ModerationCategory]:
        """Loads and parses the CSV file into ModerationCategory objects."""
        self.categories = []
        try:
            print(f"[HybridMod] Loading CSV data from {self.file_path}...", file=sys.stderr)
            with open(self.file_path, mode='r', encoding='utf-8', errors='replace') as csvfile:
                reader = csv.DictReader(csvfile)
                
                last_category = ""
                last_cat_keywords = []

                for row in reader:
                    # Skip empty rows (if completely empty)
                    if not row: continue
                    
                    # 1. Fill Down Logic for Category
                    category = row.get('Category', '').strip()
                    if not category and last_category:
                        category = last_category
                    elif category:
                        last_category = category # Update known category
                    
                    if not category:
                        # Still no category? Skip.
                        continue

                    # 2. Keywords Logic
                    raw_cat_keywords = row.get('Tokenized_category_keywords_total', '') or ""
                    cat_keywords = [k.strip().lower() for k in raw_cat_keywords.split(',') if k.strip()]
                    
                    # Fill down category keywords if empty
                    if not cat_keywords and last_cat_keywords:
                        cat_keywords = last_cat_keywords
                    elif cat_keywords:
                        last_cat_keywords = cat_keywords
                    
                    # 3. Subcategory Logic
                    # Subcategory is mandatory for a row to be a "rule"
                    subcategory = row.get('Subcategory', '').strip()
                    if not subcategory:
                         # Maybe it's a category header row only? we can add it as a generic rule or skip
                         # Usually in this format, every row with subcategory is a rule.
                         continue

                    raw_sub_keywords = row.get('Tokenized_subcategory_keywords_total', '') or ""
                    sub_keywords = [k.strip().lower() for k in raw_sub_keywords.split(',') if k.strip()]

                    # Parse Age Rules
                    age_rules = AgeRestrictionRules(
                        rules_below_10=row.get('rules_below_10', 'Block'),
                        rules_10_13=row.get('rules_10_13', 'Gate'),
                        rules_13_16=row.get('rules_13_16', 'Gate'),
                        rules_16_18=row.get('rules_16_18', 'Allow')
                    )

                    category_obj = ModerationCategory(
                        category=category,
                        subcategory=subcategory,
                        category_keywords=cat_keywords,
                        subcategory_keywords=sub_keywords,
                        age_rules=age_rules
                    )
                    self.categories.append(category_obj)
            
            print(f"[HybridMod] ✅ Successfully loaded {len(self.categories)} categories.", file=sys.stderr)
            logger.info(f"Loaded {len(self.categories)} categories from {self.file_path}")
            return self.categories

        except FileNotFoundError:
            logger.error(f"CSV file not found at {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"Error parse CSV: {e}")
            raise
