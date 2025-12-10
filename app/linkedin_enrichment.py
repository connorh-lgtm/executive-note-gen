"""
LinkedIn profile enrichment using Perplexity API
"""
import os
import openai
from app.enrichment_cache import get_cached_enrichment, cache_enrichment


def calculate_confidence(result: dict, prospect_name: str, prospect_company: str) -> int:
    """
    Calculate confidence score for enrichment results (0-100)
    
    Higher score = more confident the data is about the correct person
    """
    confidence = 100
    
    # Extract first and last name
    name_parts = prospect_name.split()
    first_name = name_parts[0].lower() if name_parts else ""
    last_name = name_parts[-1].lower() if len(name_parts) > 1 else ""
    
    unique_fact = result.get('unique_fact', '').lower()
    business_init = result.get('business_initiative', '').lower()
    linkedin_insight = result.get('linkedin_insight', '').lower()
    
    # Check if name appears in results
    name_found = False
    if first_name and first_name in unique_fact:
        name_found = True
    if last_name and last_name in unique_fact:
        name_found = True
    if prospect_name.lower() in unique_fact:
        name_found = True
    
    if not name_found:
        confidence -= 30
    
    # Check if company appears in results
    if prospect_company:
        company_found = (
            prospect_company.lower() in unique_fact or
            prospect_company.lower() in business_init or
            prospect_company.lower() in linkedin_insight
        )
        if not company_found:
            confidence -= 20
    
    # Check for generic/fallback phrases (indicates low quality)
    generic_phrases = [
        'experienced professional',
        'leader in their field',
        'driving innovation',
        'digital transformation',
        'operational excellence',
        'could not automatically enrich'
    ]
    
    for phrase in generic_phrases:
        if phrase in unique_fact or phrase in business_init:
            confidence -= 40
            break
    
    # Check for specific details (good signs)
    specific_indicators = [
        'award', 'recognition', 'named', 'finalist', 'winner',
        'led', 'launched', 'built', 'grew', 'scaled',
        'million', 'billion', '%', 'x',
        'published', 'spoke', 'presented'
    ]
    
    has_specific_details = any(indicator in unique_fact for indicator in specific_indicators)
    if has_specific_details:
        confidence += 10
    
    # Ensure confidence is between 0 and 100
    confidence = max(0, min(100, confidence))
    
    return confidence


async def enrich_linkedin_profile(
    linkedin_url: str,
    prospect_name: str,
    prospect_title: str = "",
    prospect_company: str = ""
) -> dict:
    """
    Use Perplexity to research a LinkedIn profile and extract insights
    
    Args:
        linkedin_url: LinkedIn profile URL
        prospect_name: Name of the prospect
        prospect_title: Job title (optional, helps with search)
        prospect_company: Company name (optional, helps with search)
    
    Returns:
        {
            "unique_fact": "...",
            "business_initiative": "...",
            "linkedin_insight": "...",
            "confidence": 0-100,
            "needs_verification": bool
        }
    """
    # Check cache first
    cached_result = get_cached_enrichment(linkedin_url, prospect_name)
    if cached_result:
        cached_result['from_cache'] = True
        return cached_result
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not configured. Add it to your .env file.")
    
    client = openai.AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai"
    )
    
    # Build search query
    search_context = f"{prospect_name}"
    if prospect_title:
        search_context += f", {prospect_title}"
    if prospect_company:
        search_context += f" at {prospect_company}"
    
    prompt = f"""You MUST research this EXACT LinkedIn profile URL: {linkedin_url}

The person you are researching is: {search_context}

IMPORTANT: Only return information about the person at the LinkedIn URL provided above. Do not confuse them with other people who have similar names.

Find information about THIS SPECIFIC PERSON:

1. **Unique Fact**: Find ONE specific, recent achievement, award, initiative, or interesting fact about THIS PERSON or their company. Look for:
   - Recent awards or recognition
   - Major projects or initiatives they've led
   - Company milestones or achievements
   - Speaking engagements or publications
   - Unique background or experience
   
   VERIFY: Make sure this fact is about {prospect_name}{f" at {prospect_company}" if prospect_company else ""}, not someone else.

2. **Business Initiative**: Identify current business priorities, challenges, or strategic initiatives for their company or role. Look for:
   - Digital transformation efforts
   - Technology modernization
   - Growth initiatives
   - Industry challenges they're facing
   - Strategic priorities mentioned in recent posts or articles

Return ONLY a JSON object with these fields:
{{
    "unique_fact": "Specific fact with details about {prospect_name}",
    "business_initiative": "Current business priority or challenge",
    "linkedin_insight": "Brief summary of key insights from their profile"
}}

Be specific and use recent information. If you can't find something specific about {prospect_name}, say so rather than returning information about a different person."""
    
    try:
        response = await client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "system", "content": "You are a research assistant that extracts key insights from LinkedIn profiles. You MUST only return information about the specific person at the LinkedIn URL provided. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more focused, accurate results
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON response
        import json
        import re
        
        # Remove markdown code fences if present
        content = content.strip()
        if content.startswith("```"):
            match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
            if match:
                content = match.group(1)
            else:
                content = re.sub(r'```(?:json)?', '', content).strip()
        
        result = json.loads(content)
        
        # Validate required fields
        if "unique_fact" not in result:
            result["unique_fact"] = f"{prospect_name} is a leader in their field"
        if "business_initiative" not in result:
            result["business_initiative"] = "Driving innovation and growth"
        if "linkedin_insight" not in result:
            result["linkedin_insight"] = "Experienced professional in their industry"
        
        # Calculate confidence score
        confidence = calculate_confidence(result, prospect_name, prospect_company)
        result["confidence"] = confidence
        result["needs_verification"] = confidence < 70
        
        # Cache the result
        cache_enrichment(linkedin_url, prospect_name, result)
        
        return result
        
    except Exception as e:
        # Return fallback data if enrichment fails
        return {
            "unique_fact": f"{prospect_name} is an experienced {prospect_title or 'professional'} at {prospect_company or 'their company'}",
            "business_initiative": "Driving digital transformation and operational excellence",
            "linkedin_insight": f"Could not automatically enrich profile: {str(e)}",
            "confidence": 0,
            "needs_verification": True
        }
