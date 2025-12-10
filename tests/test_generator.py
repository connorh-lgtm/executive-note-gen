"""
Test generator module with mocked LLM calls
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.generator import generate_outreach_emails


@pytest.mark.asyncio
async def test_generate_outreach_emails_cold_outreach():
    """Test cold outreach email generation"""
    # Mock the model response
    mock_response = {
        "subject": "AI Scale & Strategic Velocity",
        "body": "Hi Sarah,\n\nYour CIO of the Year recognition highlights your leadership. Scaling AI from 5 to 50 use cases requires both velocity and efficiency.\n\nDevin, the AI software engineer, has rolled out in production at Citi and Goldman Sachs. On average, banks see 6–12x efficiency gains on human engineering time with Devin.\n\nWould you be open to a quick Zoom next week?\n\nBest,\nJohn"
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await generate_outreach_emails(
            message_type="cold_outreach",
            prospect_name="Sarah Johnson",
            prospect_title="Chief Technology Officer",
            prospect_company="Acme Corp",
            unique_fact="Named CIO of the Year finalist",
            business_initiative="Scaling AI use cases from 5 to 50",
            manager_name="John Smith",
            model_provider="anthropic"
        )
        
        # Verify result structure
        assert "subject" in result
        assert "body" in result
        assert "metadata" in result
        
        # Verify metadata
        assert result["metadata"]["message_type"] == "cold_outreach"
        assert result["metadata"]["prospect_name"] == "Sarah Johnson"
        assert result["metadata"]["prospect_company"] == "Acme Corp"
        assert result["metadata"]["manager_name"] == "John Smith"
        assert result["metadata"]["model_provider"] == "anthropic"
        
        # Verify mock was called
        mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_outreach_emails_in_person_ask():
    """Test in-person ask email generation"""
    mock_response = {
        "subject": "Chicago Executive Dinner Invitation",
        "body": "Hi Jane,\n\nI'd like to invite you to a private executive dinner in Chicago on Oct 9th at 6pm at Elske.\n\nYour AI Summit keynote demonstrated thought leadership. This dinner brings together peers discussing agentic AI impact.\n\nCan I save you a seat?\n\nBest,\nJake"
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await generate_outreach_emails(
            message_type="in_person_ask",
            prospect_name="Jane Doe",
            prospect_title="CTO",
            prospect_company="Test Inc",
            unique_fact="Keynote speaker at AI Summit",
            business_initiative="Leading digital transformation",
            manager_name="Jake Smith",
            meeting_purpose="Private executive dinner in Chicago on Oct 9th at 6pm at Elske",
            model_provider="openai"
        )
        
        assert result["metadata"]["message_type"] == "in_person_ask"
        assert result["metadata"]["model_provider"] == "openai"


@pytest.mark.asyncio
async def test_generate_outreach_emails_executive_alignment():
    """Test executive alignment email generation"""
    mock_response = {
        "subject": "BMO & Devin Strategy",
        "body": "Hi Eric,\n\nCongrats on Fast Company recognition. We've met with your team about legacy migrations.\n\nDevin has rolled out at Citi and Goldman. Banks see 6–12x efficiency gains.\n\nCan our EAs coordinate a call?\n\nCheers,\nRussell"
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await generate_outreach_emails(
            message_type="executive_alignment",
            prospect_name="Eric Thompson",
            prospect_title="CIO",
            prospect_company="BMO Financial",
            unique_fact="Recognized on Fast Company list",
            business_initiative="Legacy system migrations",
            manager_name="Russell"
        )
        
        assert result["metadata"]["message_type"] == "executive_alignment"


@pytest.mark.asyncio
async def test_generate_outreach_emails_missing_subject():
    """Test error handling when model response missing subject"""
    mock_response = {
        "body": "Email body without subject"
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        with pytest.raises(ValueError, match="missing 'subject' field"):
            await generate_outreach_emails(
                message_type="cold_outreach",
                prospect_name="Test",
                prospect_title="Test",
                prospect_company="Test",
                unique_fact="Test",
                business_initiative="Test"
            )


@pytest.mark.asyncio
async def test_generate_outreach_emails_missing_body():
    """Test error handling when model response missing body"""
    mock_response = {
        "subject": "Test Subject"
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        with pytest.raises(ValueError, match="missing 'body' field"):
            await generate_outreach_emails(
                message_type="cold_outreach",
                prospect_name="Test",
                prospect_title="Test",
                prospect_company="Test",
                unique_fact="Test",
                business_initiative="Test"
            )


@pytest.mark.asyncio
async def test_generate_outreach_emails_default_manager():
    """Test generation with default manager name"""
    mock_response = {
        "subject": "Test Subject",
        "body": "Test body"
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await generate_outreach_emails(
            message_type="cold_outreach",
            prospect_name="Test",
            prospect_title="Test",
            prospect_company="Test",
            unique_fact="Test",
            business_initiative="Test"
        )
        
        assert result["metadata"]["manager_name"] == "[Manager's Name]"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
