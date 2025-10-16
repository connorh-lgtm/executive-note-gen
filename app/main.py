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
from app.bio_summarizer import (
    summarize_bio, get_cache_stats, 
    BioValidationError, BioSummarizationError
)
from app.companies_data import (
    get_all_companies, get_company, search_companies,
    create_company, update_company, delete_company
)
from typing import List

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
app.mount("/static", StaticFiles(directory=static_path), name="static")


class GenerateRequest(BaseModel):
    """Request model for email generation"""
    prospect_name: str = Field(..., min_length=1, description="Prospect's full name")
    prospect_title: str = Field(..., min_length=1, description="Prospect's job title")
    prospect_company: str = Field(..., min_length=1, description="Prospect's company name")
    unique_fact: str = Field(..., min_length=1, description="Unique fact about the prospect")
    business_initiative: str = Field(..., min_length=1, description="Business initiative or pain point")
    manager_name: str = Field(default="[Manager's Name]", description="Your name (the sender)")
    message_type: str = Field(..., description="Type of message: cold_outreach, in_person_ask, or executive_alignment")
    meeting_purpose: Optional[str] = Field(None, description="Purpose of in-person meeting (for in_person_ask type)")
    linkedin_insight: Optional[str] = Field(None, description="AI-generated insight from LinkedIn bio (optional supplement to unique_fact)")


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


class BioSummaryRequest(BaseModel):
    """Request model for bio summarization"""
    bio_text: str = Field(..., min_length=20, description="Full bio/about section text")
    prospect_name: Optional[str] = Field(None, description="Prospect name for context")
    prospect_title: Optional[str] = Field(None, description="Prospect title for context")


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
            linkedin_insight=request.linkedin_insight or "",
            model_provider="anthropic"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


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
        
        # Create feedback file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        feedback_file = os.path.join(feedback_dir, f"feedback_{timestamp}.json")
        
        # Save feedback to file
        feedback_data = request.model_dump()
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        return {"status": "success", "message": "Feedback saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")


@app.post("/api/summarize-bio")
async def summarize_bio_endpoint(request: BioSummaryRequest):
    """
    Summarize a LinkedIn bio into one compelling sentence.
    
    Returns:
        200: Success with summary
        400: Validation error (bio too short)
        500: API or processing error
    """
    try:
        summary = await summarize_bio(
            bio_text=request.bio_text,
            prospect_name=request.prospect_name or "",
            prospect_title=request.prospect_title or ""
        )
        
        return {
            "summary": summary,
            "status": "success"
        }
    except BioValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_failed",
                "message": str(e)
            }
        )
    except BioSummarizationError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "summarization_failed", 
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "unexpected_error",
                "message": f"Unexpected error during bio summarization: {str(e)}"
            }
        )


@app.get("/api/bio-cache-stats")
async def bio_cache_stats():
    """
    Get bio summarization cache performance statistics
    """
    return get_cache_stats()


# ============================================================================
# Prospect Research Endpoints
# ============================================================================

from app.researcher import research_prospect, get_research_cache_stats


class ResearchRequest(BaseModel):
    """Request model for prospect research"""
    name: str = Field(..., min_length=1, description="Prospect's full name")
    title: str = Field("", description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")


@app.post("/api/research-prospect")
async def research_prospect_endpoint(request: ResearchRequest):
    """
    Research a prospect using Perplexity API with web search
    
    Finds compelling facts about the prospect including:
    - Blog posts and articles about AI/technology
    - Speaking engagements and presentations
    - Awards and recognition
    - Company initiatives they've led
    - Media quotes and interviews
    
    Results are cached for 7 days to minimize API costs.
    """
    try:
        results = await research_prospect(
            name=request.name,
            title=request.title,
            company=request.company,
            linkedin_url=request.linkedin_url
        )
        
        return {
            "success": True,
            "data": results
        }
        
    except ValueError as e:
        # API key not configured
        raise HTTPException(
            status_code=500,
            detail={
                "error": "configuration_error",
                "message": str(e)
            }
        )
    except Exception as e:
        print(f"Error in research endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "research_failed",
                "message": f"Failed to research prospect: {str(e)}"
            }
        )


@app.get("/api/research-cache-stats")
async def research_cache_stats():
    """
    Get prospect research cache performance statistics
    """
    return get_research_cache_stats()


# ============================================================================
# Company & Initiatives Management Endpoints
# ============================================================================

class CompanyCreate(BaseModel):
    """Request model for creating a company"""
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    industry: Optional[str] = Field("", max_length=100, description="Industry/sector")
    initiatives: Optional[List[str]] = Field(default=[], description="List of up to 3 initiatives")


class CompanyUpdate(BaseModel):
    """Request model for updating a company"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    initiatives: Optional[List[str]] = Field(None, description="List of up to 3 initiatives")


@app.get("/api/companies")
async def list_companies():
    """Get all companies with their initiatives"""
    companies = get_all_companies()
    return {"companies": companies}


@app.get("/api/companies/search")
async def search_companies_endpoint(q: str):
    """Search companies by name (autocomplete)"""
    if len(q) < 2:
        return {"companies": []}
    results = search_companies(q)
    return {"companies": results}


@app.get("/api/companies/{company_id}")
async def get_company_endpoint(company_id: str):
    """Get company by ID with all details"""
    company = get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.post("/api/companies", status_code=201)
async def create_company_endpoint(company: CompanyCreate):
    """Create a new company"""
    try:
        new_company = create_company(
            name=company.name,
            industry=company.industry or "",
            initiatives=company.initiatives or []
        )
        return new_company
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/companies/{company_id}")
async def update_company_endpoint(company_id: str, company: CompanyUpdate):
    """Update company details"""
    try:
        updated = update_company(
            company_id=company_id,
            name=company.name,
            industry=company.industry,
            initiatives=company.initiatives
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Company not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/companies/{company_id}", status_code=204)
async def delete_company_endpoint(company_id: str):
    """Delete a company and all its initiatives"""
    success = delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
