"""
LinkedIn profile enrichment using Perplexity API
"""
import os
import openai


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
            "linkedin_insight": "..."
        }
    """
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
        
        return result
        
    except Exception as e:
        # Return fallback data if enrichment fails
        return {
            "unique_fact": f"{prospect_name} is an experienced {prospect_title or 'professional'} at {prospect_company or 'their company'}",
            "business_initiative": "Driving digital transformation and operational excellence",
            "linkedin_insight": f"Could not automatically enrich profile: {str(e)}"
        }
