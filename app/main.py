"""
FastAPI backend for Executive Note Generator
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.generator import generate_outreach_emails
from app.linkedin_enrichment import enrich_linkedin_profile

app = FastAPI(title="Executive Note Generator", version="1.0.0")

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


class GenerateResponse(BaseModel):
    """Response model with single email template"""
    subject: str
    body: str
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
async def generate(request: GenerateRequest):
    """
    Generate 1 optimized executive outreach email template
    """
    try:
        result = await generate_outreach_emails(
            message_type=request.message_type,
            prospect_name=request.prospect_name,
            prospect_title=request.prospect_title,
            prospect_company=request.prospect_company,
            unique_fact=request.unique_fact,
            business_initiative=request.business_initiative,
            manager_name=request.manager_name,
            meeting_purpose=request.meeting_purpose,
            model_provider="anthropic"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/api/enrich")
async def enrich_profile(linkedin_url: str, prospect_name: str, prospect_title: str = "", prospect_company: str = ""):
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
async def summarize_bio(request: dict):
    """
    Legacy endpoint - alias for /api/enrich
    Summarize LinkedIn bio using Perplexity API
    Accepts JSON body for compatibility with Chrome extension
    """
    try:
        # Log the incoming request for debugging
        print(f"Received summarize-bio request: {request}")
        
        # Extract fields with fallbacks
        linkedin_url = request.get('linkedin_url') or request.get('linkedinUrl', '')
        prospect_name = request.get('prospect_name') or request.get('prospectName', '')
        prospect_title = request.get('prospect_title') or request.get('prospectTitle', '')
        prospect_company = request.get('prospect_company') or request.get('prospectCompany', '')
        
        if not linkedin_url or not prospect_name:
            return {
                "unique_fact": f"{prospect_name or 'Professional'} is an experienced leader in their field",
                "business_initiative": "Driving digital transformation and operational excellence",
                "linkedin_insight": "Missing required fields: linkedin_url or prospect_name"
            }
        
        result = await enrich_profile(
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
async def submit_feedback(request: FeedbackRequest):
    """
    Save user feedback for improving future outputs
    """
    import json
    from datetime import datetime
    
    try:
        # Create feedback directory if it doesn't exist
        feedback_dir = os.path.join(os.path.dirname(__file__), "..", "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Create feedback file path with timestamp (include microseconds to avoid collisions)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        feedback_file = os.path.join(feedback_dir, f"feedback_{timestamp}.json")
        
        # Save feedback to file
        feedback_data = request.model_dump()
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        return {"status": "success", "message": "Feedback saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
