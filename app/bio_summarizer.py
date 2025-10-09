"""
Bio summarization using Claude API
"""
from app.model_client import call_anthropic_text


async def summarize_bio(bio_text: str, prospect_name: str = "", prospect_title: str = "") -> str:
    """
    Summarize a LinkedIn bio into one compelling sentence for unique fact
    
    Args:
        bio_text: The full bio/about section text
        prospect_name: Optional prospect name for context
        prospect_title: Optional prospect title for context
    
    Returns:
        A single sentence unique fact (max 100 words)
    """
    if not bio_text or len(bio_text.strip()) < 20:
        return ""
    
    system_prompt = """You are an expert at extracting the most interesting and relevant facts from executive bios.
Your job is to read a LinkedIn bio and extract ONE compelling fact that would be useful for personalized outreach.

Focus on:
- Unique career achievements or transitions
- Interesting background or origin story
- Notable companies or roles
- Specific initiatives they've led
- Relevant interests or expertise
- Geographic connections or experiences

Avoid:
- Generic statements ("experienced leader")
- Buzzwords without substance
- Multiple facts (pick the BEST one)
- Long explanations (keep it concise)

Output format: One sentence, 15-30 words, factual and specific."""

    context = ""
    if prospect_name:
        context += f"Prospect: {prospect_name}\n"
    if prospect_title:
        context += f"Title: {prospect_title}\n"
    
    user_prompt = f"""{context}
Bio text:
{bio_text[:1000]}

Extract ONE compelling unique fact as a single sentence (15-30 words).
Return ONLY the sentence, no explanation or preamble."""

    try:
        print(f"Summarizing bio for {prospect_name}, length: {len(bio_text)}")
        
        summary = await call_anthropic_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="claude-sonnet-4-20250514"
        )
        
        print(f"API returned summary: {summary}")
        
        # Clean up any quotes or extra formatting
        summary = summary.strip().strip('"').strip("'").strip()
        
        # Limit to reasonable length
        if len(summary) > 200:
            summary = summary[:200].rsplit(' ', 1)[0] + '...'
        
        return summary
        
    except Exception as e:
        print(f"Error summarizing bio: {e}")
        import traceback
        traceback.print_exc()
        return ""
