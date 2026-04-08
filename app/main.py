"""
FastAPI backend for Executive Note Generator
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env file
load_dotenv()

from app.generator import generate_outreach_emails
from app.linkedin_enrichment import enrich_linkedin_profile

# Rate limit configuration (configurable via environment variables)
GENERATE_RATE_LIMIT = os.getenv("GENERATE_RATE_LIMIT", "10/minute")
ENRICH_RATE_LIMIT = os.getenv("ENRICH_RATE_LIMIT", "20/minute")
FEEDBACK_RATE_LIMIT = os.getenv("FEEDBACK_RATE_LIMIT", "30/minute")

app = FastAPI(title="Executive Note Generator", version="1.0.0")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


class GenerateRequest(BaseModel):
    """Request model for email generation"""
    message_type: str = Field(..., description="Message type: cold_outreach, in_person_ask, or executive_alignment")
    prospect_name: str = Field(..., min_length=1, max_length=100, description="Prospect's full name")
    prospect_title: str = Field(..., min_length=1, max_length=150, description="Prospect's job title")
    prospect_company: str = Field(..., min_length=1, max_length=150, description="Prospect's company")
    unique_fact: str = Field(..., min_length=1, max_length=500, description="Unique fact about prospect or company")
    business_initiative: str = Field(..., min_length=1, max_length=500, description="Business initiative or challenge")
    manager_name: str = Field(default="[Manager's Name]", max_length=100, description="Name of email sender")
    meeting_purpose: str = Field(default="", max_length=500, description="Purpose of in-person meeting (for in_person_ask type)")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL for auto-enrichment")


class EmailTemplate(BaseModel):
    """Single email template"""
    angle: str
    subject: str
    body: str


class GenerateResponse(BaseModel):
    """Response model with 5 email templates"""
    templates: list[EmailTemplate]
    metadata: dict


class FeedbackRequest(BaseModel):
    """Request model for feedback submission"""
    feedback_type: str = Field(..., description="positive or negative")
    original_output: dict = Field(..., description="Original generated output")
    improved_version: Optional[str] = Field(None, description="User's improved version")
    metadata: dict = Field(..., description="Generation metadata")
    timestamp: str = Field(..., description="ISO timestamp")


@app.get("/")
async def root():
    """Serve the landing page"""
    index_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Executive Note Generator API", "docs": "/docs"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "executive-note-gen"}


@app.post("/api/generate", response_model=GenerateResponse)
@limiter.limit(GENERATE_RATE_LIMIT)
async def generate(request: Request, body: GenerateRequest):
    """
    Generate 5 optimized executive outreach email templates
    """
    try:
        result = await generate_outreach_emails(
            message_type=body.message_type,
            prospect_name=body.prospect_name,
            prospect_title=body.prospect_title,
            prospect_company=body.prospect_company,
            unique_fact=body.unique_fact,
            business_initiative=body.business_initiative,
            manager_name=body.manager_name,
            meeting_purpose=body.meeting_purpose
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/api/enrich")
@limiter.limit(ENRICH_RATE_LIMIT)
async def enrich_profile(request: Request, linkedin_url: str, prospect_name: str, prospect_title: str = "", prospect_company: str = ""):
    """
    Enrich LinkedIn profile using Perplexity API
    """
    try:
        result = await enrich_linkedin_profile(
            linkedin_url=linkedin_url,
            prospect_name=prospect_name,
            prospect_title=prospect_title,
            prospect_company=prospect_company
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


class EnrichRequest(BaseModel):
    """Request model for LinkedIn enrichment"""
    linkedin_url: str = Field(..., description="LinkedIn profile URL")
    prospect_name: str = Field(..., description="Prospect's name")
    prospect_title: str = Field(default="", description="Prospect's job title")
    prospect_company: str = Field(default="", description="Prospect's company")
    
    class Config:
        # Allow extra fields from Chrome extension
        extra = "allow"


@app.post("/api/summarize-bio")
@limiter.limit(ENRICH_RATE_LIMIT)
async def summarize_bio(request: Request, body: dict):
    """
    Legacy endpoint - alias for /api/enrich
    Summarize LinkedIn bio using Perplexity API
    Accepts JSON body for compatibility with Chrome extension
    """
    try:
        # Log the incoming request for debugging
        print(f"Received summarize-bio request: {body}")
        
        # Extract fields with fallbacks
        linkedin_url = body.get('linkedin_url') or body.get('linkedinUrl', '')
        prospect_name = body.get('prospect_name') or body.get('prospectName', '')
        prospect_title = body.get('prospect_title') or body.get('prospectTitle', '')
        prospect_company = body.get('prospect_company') or body.get('prospectCompany', '')
        
        if not linkedin_url or not prospect_name:
            return {
                "unique_fact": f"{prospect_name or 'Professional'} is an experienced leader in their field",
                "business_initiative": "Driving digital transformation and operational excellence",
                "linkedin_insight": "Missing required fields: linkedin_url or prospect_name"
            }
        
        result = await enrich_linkedin_profile(
            linkedin_url=linkedin_url,
            prospect_name=prospect_name,
            prospect_title=prospect_title,
            prospect_company=prospect_company
        )
        return result
    except Exception as e:
        # Log the error for debugging
        print(f"Enrichment error: {str(e)}")
        # Return fallback data instead of failing
        return {
            "unique_fact": f"Experienced professional in their field",
            "business_initiative": "Driving digital transformation and operational excellence",
            "linkedin_insight": f"Enrichment failed: {str(e)}"
        }


@app.post("/api/feedback")
@limiter.limit(FEEDBACK_RATE_LIMIT)
async def submit_feedback(request: Request, body: FeedbackRequest):
    """
    Save user feedback for improving future outputs
    """
    import json
    from datetime import datetime
    
    try:
        # Create feedback directory if it doesn't exist
        feedback_dir = os.path.join(os.path.dirname(__file__), "..", "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Create feedback file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        feedback_file = os.path.join(feedback_dir, f"feedback_{timestamp}.json")
        
        # Save feedback to file
        feedback_data = body.model_dump()
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        return {"status": "success", "message": "Feedback saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
