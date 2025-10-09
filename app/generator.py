"""
Core generation logic for executive outreach emails
"""
from typing import Optional
from app.prompts_v2 import build_prompt
from app.model_client import generate_with_model


async def generate_outreach_emails(
    message_type: str,
    prospect_name: str,
    prospect_title: str,
    prospect_company: str,
    unique_fact: str,
    business_initiative: str,
    manager_name: str = "[Manager's Name]",
    meeting_purpose: str = "",
    linkedin_insight: str = "",
    model_provider: str = "anthropic"
) -> dict:
    """
    Generate 1 optimized executive outreach email using mega-prompt v14
    
    Args:
        message_type: cold_outreach, in_person_ask, or executive_alignment
        prospect_name: Full name of the prospect
        prospect_title: Job title of the prospect
        prospect_company: Company name
        unique_fact: Unique fact about prospect or company (award, initiative, etc.)
        business_initiative: Business initiative or challenge
        manager_name: Name of the email sender (executive)
        model_provider: "openai" or "anthropic"
    
    Returns:
        {
            "subject": "...",
            "body": "...",
            "metadata": {
                "message_type": "...",
                "prospect_name": "...",
                "prospect_company": "...",
                "manager_name": "...",
                "model_provider": "..."
            }
        }
    """
    # Build prompts from mega-prompt template
    system_prompt, user_prompt = build_prompt(
        message_type=message_type,
        prospect_name=prospect_name,
        prospect_title=prospect_title,
        prospect_company=prospect_company,
        unique_fact=unique_fact,
        business_initiative=business_initiative,
        manager_name=manager_name,
        meeting_purpose=meeting_purpose,
        linkedin_insight=linkedin_insight
    )
    
    # Generate with selected model provider
    result = await generate_with_model(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        provider=model_provider
    )
    
    # Validate response structure
    print(f"Model returned: {result}")
    
    if "subject" not in result:
        raise ValueError("Model response missing 'subject' field")
    
    if "body" not in result:
        print(f"ERROR: Model response missing 'body' field. Full response: {result}")
        raise ValueError("Model response missing 'body' field")
    
    # Add metadata
    result["metadata"] = {
        "message_type": message_type,
        "prospect_name": prospect_name,
        "prospect_company": prospect_company,
        "manager_name": manager_name,
        "model_provider": model_provider
    }
    
    return result
