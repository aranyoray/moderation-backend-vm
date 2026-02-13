from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
import sys

# Add current directory to path so we can import hybrid_moderation
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hybrid_moderation.core import ContentModerationSystem
from hybrid_moderation.models import ModerationResult
from hybrid_moderation.config import SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("moderation-api")

app = FastAPI(title="Komal Hybrid Moderation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "x-api-key"],
)
app.state.system_prompt = SYSTEM_PROMPT

# Initialize CMS
cms = ContentModerationSystem(csv_path="Models_Masterdoc_Test.csv")
try:
    cms.initialize()
    logger.info("Content Moderation System initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CMS: {e}")
    sys.exit(1)

class AnalysisRequest(BaseModel):
    text: str
    age_group: str = '13-16'
    content_id: str = 'api-request'

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "komal-moderation"}

@app.post("/analyze")
def analyze_content(request: AnalysisRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Text content is required")
    
    try:
        logger.info(f"Analyzing content ID: {request.content_id}, Age: {request.age_group}")
        result = cms.analyze(request.content_id, request.text, request.age_group)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
