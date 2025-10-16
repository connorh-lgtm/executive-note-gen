"""
Prospect research using Perplexity API with web search
"""
import os
import re
import hashlib
from typing import Optional, List, Dict
from collections import OrderedDict
from datetime import datetime, timedelta

# Perplexity uses OpenAI SDK
try:
    from openai import AsyncOpenAI
except ImportError:
    raise ImportError("openai package required. Run: pip install openai")


# Initialize Perplexity client
def get_perplexity_client():
    """Get Perplexity API client"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not set in environment variables")
    
    return AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai"
    )


# Cache configuration
MAX_CACHE_SIZE = 500
CACHE_TTL_DAYS = 7

_research_cache = OrderedDict()
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "evictions": 0
}


def _get_cache_key(name: str, company: str) -> str:
    """Generate cache key from name and company"""
    return hashlib.sha256(f"{name.lower()}|{company.lower()}".encode()).hexdigest()


def _is_cache_valid(cached_data: dict) -> bool:
    """Check if cached data is still valid (within TTL)"""
    if "timestamp" not in cached_data:
        return False
    
    cached_time = datetime.fromisoformat(cached_data["timestamp"])
    age = datetime.utcnow() - cached_time
    return age < timedelta(days=CACHE_TTL_DAYS)


def _add_to_cache(cache_key: str, data: dict):
    """Add research results to cache with LRU eviction"""
    # Evict oldest if cache is full
    if len(_research_cache) >= MAX_CACHE_SIZE:
        evicted_key = next(iter(_research_cache))
        _research_cache.pop(evicted_key)
        _cache_stats["evictions"] += 1
        print(f"Research cache full, evicted oldest entry")
    
    # Add timestamp
    data["timestamp"] = datetime.utcnow().isoformat()
    _research_cache[cache_key] = data
    _research_cache.move_to_end(cache_key)


def get_research_cache_stats() -> dict:
    """Get research cache statistics"""
    total = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total * 100) if total > 0 else 0
    
    return {
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "evictions": _cache_stats["evictions"],
        "hit_rate_percent": round(hit_rate, 2),
        "cache_size": len(_research_cache),
        "max_cache_size": MAX_CACHE_SIZE,
        "ttl_days": CACHE_TTL_DAYS
    }


def parse_research_findings(content: str) -> List[Dict[str, str]]:
    """
    Parse Perplexity response into structured findings
    
    Args:
        content: Raw response from Perplexity
    
    Returns:
        List of findings with fact, source, and confidence
    """
    findings = []
    
    # Split by numbered items or bullet points
    # Look for patterns like "1.", "2.", "-", "•"
    lines = content.split('\n')
    
    current_fact = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a new item (numbered or bulleted)
        if re.match(r'^\d+\.|\-|\•', line):
            # Save previous fact if exists
            if current_fact:
                fact_text = ' '.join(current_fact)
                if len(fact_text) > 20:  # Minimum length
                    findings.append({
                        "fact": fact_text,
                        "confidence": "high" if len(fact_text) > 50 else "medium"
                    })
            # Start new fact
            current_fact = [re.sub(r'^\d+\.|\-|\•', '', line).strip()]
        else:
            # Continue current fact
            if current_fact:
                current_fact.append(line)
    
    # Add last fact
    if current_fact:
        fact_text = ' '.join(current_fact)
        if len(fact_text) > 20:
            findings.append({
                "fact": fact_text,
                "confidence": "high" if len(fact_text) > 50 else "medium"
            })
    
    # If no structured findings found, treat whole response as one finding
    if not findings and len(content) > 50:
        findings.append({
            "fact": content.strip(),
            "confidence": "medium"
        })
    
    return findings[:5]  # Return max 5 findings


async def research_prospect(
    name: str,
    title: str,
    company: str,
    linkedin_url: Optional[str] = None
) -> dict:
    """
    Research a prospect using Perplexity API with web search
    
    Args:
        name: Prospect's full name
        title: Job title
        company: Company name
        linkedin_url: Optional LinkedIn profile URL
    
    Returns:
        {
            "findings": [
                {
                    "fact": "Led AI transformation initiative...",
                    "confidence": "high"
                }
            ],
            "raw_response": "Full Perplexity response",
            "citations": ["url1", "url2"],
            "cached": False,
            "timestamp": "2024-10-16T15:30:00"
        }
    """
    # Check cache first
    cache_key = _get_cache_key(name, company)
    
    if cache_key in _research_cache:
        cached_data = _research_cache[cache_key]
        if _is_cache_valid(cached_data):
            _cache_stats["hits"] += 1
            print(f"Research cache hit for {name} at {company}")
            _research_cache.move_to_end(cache_key)  # Mark as recently used
            cached_data["cached"] = True
            return cached_data
        else:
            # Expired, remove from cache
            _research_cache.pop(cache_key)
            print(f"Research cache expired for {name} at {company}")
    
    _cache_stats["misses"] += 1
    print(f"Research cache miss for {name} at {company}, calling Perplexity API")
    
    # Build research prompt
    prompt = f"""Research {name}, {title} at {company}.

Find 2-4 compelling unique facts about them suitable for executive outreach emails:

Focus areas:
- Blog posts or articles they have written about AI, technology, digital transformation, or innovation
- Speaking engagements at conferences or industry events
- Awards, recognition, or industry accolades
- Major company initiatives, projects, or transformations they have led
- Quotes or interviews in major publications (Forbes, TechCrunch, etc.)
- Thought leadership on LinkedIn or other platforms

For each fact:
1. Make it specific and compelling (not generic like "experienced leader")
2. Include context that shows why it matters
3. Focus on recent content (last 2-3 years preferred)
4. Emphasize AI, technology, and digital transformation topics

Return 2-4 facts as a numbered list. Each fact should be 1-2 sentences.
If you cannot find substantial information, say so clearly rather than making generic statements."""

    try:
        client = get_perplexity_client()
        
        response = await client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",  # Has web search
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant specializing in finding compelling, specific facts about executives for business outreach. Focus on AI, technology, and digital transformation topics. Be factual and cite sources. If you cannot find substantial information, say so clearly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Lower for more factual responses
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        print(f"Perplexity research response for {name}: {len(content)} chars")
        
        # Parse findings
        findings = parse_research_findings(content)
        
        # Extract citations if available
        citations = []
        if hasattr(response, 'citations'):
            citations = response.citations
        
        result = {
            "findings": findings,
            "raw_response": content,
            "citations": citations,
            "cached": False,
            "timestamp": datetime.utcnow().isoformat(),
            "prospect_name": name,
            "prospect_company": company
        }
        
        # Add to cache
        _add_to_cache(cache_key, result)
        
        return result
        
    except Exception as e:
        print(f"Error researching prospect: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error result
        return {
            "findings": [],
            "raw_response": "",
            "citations": [],
            "cached": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def research_prospect_simple(name: str, company: str) -> List[str]:
    """
    Simplified research function that returns just a list of fact strings
    
    Args:
        name: Prospect name
        company: Company name
    
    Returns:
        List of fact strings
    """
    result = await research_prospect(name=name, title="", company=company)
    return [f["fact"] for f in result.get("findings", [])]
