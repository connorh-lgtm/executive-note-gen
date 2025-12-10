"""
Simple cache for LinkedIn enrichment results
"""
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional


CACHE_FILE = "enrichment_cache.json"
CACHE_DURATION_DAYS = 30


def _get_cache_key(linkedin_url: str, prospect_name: str) -> str:
    """Generate a cache key from LinkedIn URL and prospect name"""
    key_string = f"{linkedin_url}:{prospect_name}".lower()
    return hashlib.md5(key_string.encode()).hexdigest()


def _load_cache() -> dict:
    """Load cache from file"""
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_cache(cache: dict) -> None:
    """Save cache to file"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except IOError:
        pass  # Fail silently if we can't write cache


def get_cached_enrichment(linkedin_url: str, prospect_name: str) -> Optional[dict]:
    """
    Get cached enrichment result if available and not expired
    
    Args:
        linkedin_url: LinkedIn profile URL
        prospect_name: Prospect's name
    
    Returns:
        Cached result dict or None if not found/expired
    """
    cache = _load_cache()
    cache_key = _get_cache_key(linkedin_url, prospect_name)
    
    if cache_key not in cache:
        return None
    
    entry = cache[cache_key]
    
    # Check if expired
    cached_date = datetime.fromisoformat(entry['cached_at'])
    expiry_date = cached_date + timedelta(days=CACHE_DURATION_DAYS)
    
    if datetime.now() > expiry_date:
        # Expired, remove from cache
        del cache[cache_key]
        _save_cache(cache)
        return None
    
    return entry['result']


def cache_enrichment(linkedin_url: str, prospect_name: str, result: dict) -> None:
    """
    Cache an enrichment result
    
    Args:
        linkedin_url: LinkedIn profile URL
        prospect_name: Prospect's name
        result: Enrichment result to cache
    """
    cache = _load_cache()
    cache_key = _get_cache_key(linkedin_url, prospect_name)
    
    cache[cache_key] = {
        'linkedin_url': linkedin_url,
        'prospect_name': prospect_name,
        'result': result,
        'cached_at': datetime.now().isoformat()
    }
    
    _save_cache(cache)


def clear_cache() -> None:
    """Clear all cached enrichment results"""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
