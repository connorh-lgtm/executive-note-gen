import pytest
from unittest.mock import patch, AsyncMock
from app.bio_summarizer import summarize_bio, _bio_summary_cache


@pytest.mark.asyncio
async def test_bio_summarization_caching():
    """Test that identical bios return cached results without making duplicate API calls"""
    
    _bio_summary_cache.clear()
    
    test_bio = """John Smith is a seasoned technology executive with over 20 years of experience 
    leading digital transformation initiatives at Fortune 500 companies. He previously served as 
    CTO at Global Tech Corp where he spearheaded the migration of legacy systems to cloud infrastructure, 
    resulting in 40% cost savings. John holds an MBA from Stanford and a BS in Computer Science from MIT. 
    He is passionate about AI ethics and serves on the board of the AI Safety Institute."""
    
    mock_summary = "Former CTO at Global Tech Corp who led cloud migration saving 40% in costs"
    
    with patch('app.bio_summarizer.call_anthropic_text', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = mock_summary
        
        first_call = await summarize_bio(test_bio, "John Smith", "CTO")
        
        assert first_call == mock_summary
        assert len(_bio_summary_cache) == 1
        assert mock_api.call_count == 1
        
        second_call = await summarize_bio(test_bio, "John Smith", "CTO")
        
        assert second_call == first_call
        assert second_call == mock_summary
        assert len(_bio_summary_cache) == 1
        assert mock_api.call_count == 1


@pytest.mark.asyncio
async def test_different_bios_not_cached():
    """Test that different bios are not confused in cache"""
    
    _bio_summary_cache.clear()
    
    bio1 = "Jane Doe is a pioneering AI researcher at MIT with groundbreaking work in neural networks."
    bio2 = "Bob Johnson is a financial executive who transformed the banking industry with mobile payments."
    
    with patch('app.bio_summarizer.call_anthropic_text', new_callable=AsyncMock) as mock_api:
        mock_api.side_effect = [
            "AI researcher at MIT pioneering neural network research",
            "Financial executive who transformed banking with mobile payments"
        ]
        
        result1 = await summarize_bio(bio1, "Jane Doe", "AI Researcher")
        result2 = await summarize_bio(bio2, "Bob Johnson", "CFO")
        
        assert result1 != result2
        assert len(_bio_summary_cache) == 2
        assert mock_api.call_count == 2


@pytest.mark.asyncio
async def test_empty_bio_returns_empty_string():
    """Test that empty or very short bios return empty string"""
    
    _bio_summary_cache.clear()
    
    result = await summarize_bio("", "Test User", "CEO")
    assert result == ""
    
    result = await summarize_bio("Short", "Test User", "CEO")
    assert result == ""
    
    assert len(_bio_summary_cache) == 0


@pytest.mark.asyncio
async def test_cache_key_based_on_truncated_bio():
    """Test that cache key is based on truncated bio, not full bio"""
    
    _bio_summary_cache.clear()
    
    short_bio = "Test bio content that is under 1000 characters."
    long_bio = short_bio + (" " * 2000) + "This extra content should be truncated."
    
    with patch('app.bio_summarizer.call_anthropic_text', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = "Test summary"
        
        result1 = await summarize_bio(short_bio, "Test", "CEO")
        
        assert mock_api.call_count == 1
        
        result2 = await summarize_bio(short_bio, "Test", "CEO")
        
        assert mock_api.call_count == 1
        assert result1 == result2
