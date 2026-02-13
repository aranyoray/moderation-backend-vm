
# Configuration for Hybrid Content Moderation System

# Neutral identity terms should not drive moderation decisions on their own.
NEUTRAL_IDENTITY_TERMS = {
    "woman",
    "man",
    "girl",
    "boy",
    "child",
    "person",
}

# System prompt guidance for the moderation service (LLM-backed or rule-based).
SYSTEM_PROMPT = (
    "You are a child-safety moderation system. Treat neutral identity terms "
    "(e.g., woman, man, girl, boy, child, person) as ALWAYS SAFE when they "
    "appear alone or without harmful context. Only reduce safety scores when "
    "there is explicit harmful context such as pornography, exploitation, "
    "self-harm, or violence. For standalone neutral identity terms, return "
    "ALLOW for all age bands with a 100/100 safety score."
)

# Weights
CSV_WEIGHT = 0.30
VECTOR_WEIGHT = 0.70

# Thresholds
PRIMARY_CATEGORY_CONFIDENCE_THRESHOLD = 0.9
SUBCATEGORY_CONFIDENCE_THRESHOLD = 0.9
FINAL_SCORE_FLAG_THRESHOLD = 0.9
FINAL_SCORE_REVIEW_THRESHOLD = 0.7

# File Paths
CSV_FILE_PATH = "Models_Masterdoc_Test.csv"
