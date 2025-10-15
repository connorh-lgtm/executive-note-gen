"""
Bio summarization using Claude API
"""
import re
import hashlib
from collections import OrderedDict
from typing import Tuple
from app.model_client import call_anthropic_text

# Cache configuration
MAX_CACHE_SIZE = 1000
_bio_summary_cache = OrderedDict()

# Cache metrics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "evictions": 0
}


def truncate_at_sentence_boundary(text: str, max_chars: int = 1000, search_range: int = 200) -> str:
    """
    Truncate text at the last complete sentence within the character limit.
    
    Args:
        text: The text to truncate
        max_chars: Target maximum character count
        search_range: Additional characters to search for sentence boundaries
    
    Returns:
        Truncated text ending at a sentence boundary when possible
    """
    if len(text) <= max_chars:
        return text
    
    search_end = min(len(text), max_chars + search_range)
    search_text = text[:search_end]
    
    sentence_endings = [m.end() for m in re.finditer(r'[.!?]\s', search_text)]
    
    valid_endings = [pos for pos in sentence_endings if pos <= max_chars + search_range]
    
    if valid_endings:
        last_sentence_end = valid_endings[-1]
        return text[:last_sentence_end].rstrip()
    
    return text[:max_chars]


def _validate_summary(summary: str) -> Tuple[bool, str]:
    """
    Validate LLM-generated bio summary.
    
    Args:
        summary: The summary text to validate
    
    Returns:
        Tuple of (is_valid, validated_summary or empty string)
    """
    # Clean up formatting
    summary = summary.strip().strip('"').strip("'").strip()
    
    # Check 1: Empty or whitespace-only
    if not summary or not summary.strip():
        print("Validation failed: Empty or whitespace-only response")
        return False, ""
    
    # Check 2: Word count (5-40 words)
    word_count = len(summary.split())
    if word_count < 5:
        print(f"Validation failed: Response too short ({word_count} words, minimum 5)")
        return False, ""
    elif word_count > 40:
        print(f"Validation failed: Response too long ({word_count} words, maximum 40)")
        return False, ""
    
    # Check 3: Refusal patterns
    refusal_patterns = [
        "i cannot", "i'm unable", "i can't", "i am unable",
        "i apologize", "i'm sorry", "i am sorry",
        "as an ai", "as a language model",
        "i don't have", "i do not have", "i'm not able"
    ]
    summary_lower = summary.lower()
    if any(pattern in summary_lower for pattern in refusal_patterns):
        print("Validation failed: Refusal message detected in response")
        return False, ""
    
    # Check 4: Error patterns
    error_patterns = [
        "error occurred", "unable to extract", "could not find",
        "cannot provide", "not available", "no information",
        "insufficient information", "cannot determine"
    ]
    if any(pattern in summary_lower for pattern in error_patterns):
        print("Validation failed: Error pattern detected in response")
        return False, ""
    
    # Check 5: Character limit with smart truncation
    if len(summary) > 200:
        summary = summary[:200].rsplit(' ', 1)[0] + '...'
    
    return True, summary


def _add_to_cache(cache_key: str, summary: str):
    """
    Add entry to cache with LRU eviction.
    
    Args:
        cache_key: The cache key (hash)
        summary: The summary to cache
    """
    # Evict oldest entry if cache is full
    if len(_bio_summary_cache) >= MAX_CACHE_SIZE:
        evicted_key = next(iter(_bio_summary_cache))
        _bio_summary_cache.pop(evicted_key)
        _cache_stats["evictions"] += 1
        print(f"Cache full, evicted oldest entry (total evictions: {_cache_stats['evictions']})")
    
    _bio_summary_cache[cache_key] = summary
    # Move to end (most recently used)
    _bio_summary_cache.move_to_end(cache_key)


def get_cache_stats() -> dict:
    """
    Get cache performance statistics.
    
    Returns:
        Dictionary with cache metrics
    """
    total_requests = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "evictions": _cache_stats["evictions"],
        "hit_rate_percent": round(hit_rate, 2),
        "cache_size": len(_bio_summary_cache),
        "max_cache_size": MAX_CACHE_SIZE
    }


async def summarize_bio(bio_text: str, prospect_name: str = "", prospect_title: str = "") -> str:
    """
    Summarize a LinkedIn bio into one compelling sentence for unique fact.
    
    Uses LRU cache to avoid redundant API calls. Cache is limited to 1000 entries
    and automatically evicts oldest entries when full.
    
    Args:
        bio_text: The full bio/about section text
        prospect_name: Optional prospect name for context
        prospect_title: Optional prospect title for context
    
    Returns:
        A single sentence unique fact (max 100 words), or empty string if validation fails
    """
    if not bio_text or len(bio_text.strip()) < 20:
        return ""
    
    truncated_bio = truncate_at_sentence_boundary(bio_text, max_chars=1000, search_range=200)
    
    # Include prospect context in cache key for better personalization
    cache_input = f"{truncated_bio}|{prospect_name}|{prospect_title}"
    cache_key = hashlib.sha256(cache_input.encode('utf-8')).hexdigest()
    
    # Check cache
    if cache_key in _bio_summary_cache:
        _cache_stats["hits"] += 1
        print(f"Cache hit for bio (hash: {cache_key[:8]}...) - Hit rate: {get_cache_stats()['hit_rate_percent']}%")
        # Move to end (mark as recently used)
        _bio_summary_cache.move_to_end(cache_key)
        return _bio_summary_cache[cache_key]
    
    _cache_stats["misses"] += 1
    print(f"Cache miss for bio (hash: {cache_key[:8]}...), calling LLM - Hit rate: {get_cache_stats()['hit_rate_percent']}%")
    
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
{truncated_bio}

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
        
        # Validate summary
        _, validated_summary = _validate_summary(summary)
        
        # Add to cache (even if validation failed, to avoid re-trying bad inputs)
        _add_to_cache(cache_key, validated_summary)
        
        return validated_summary
        
    except Exception as e:
        print(f"Error summarizing bio: {e}")
        import traceback
        traceback.print_exc()
        return ""
