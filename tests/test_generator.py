"""
Test generator module with mocked LLM calls
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.generator import generate_outreach_emails


def _make_mock_templates():
    """Helper to create a standard 5-template mock response"""
    return {
        "templates": [
            {
                "angle": "Strategy & Digital Leadership",
                "subject": "AI Scale & Strategic Velocity",
                "body": "Hi Sarah,\n\nYour CIO of the Year recognition highlights your leadership in strategy.\n\nDevin has rolled out at Citi and Goldman Sachs. Banks see 6-12x efficiency gains.\n\nWould you be open to a quick Zoom next week?\n\nBest,\nJohn"
            },
            {
                "angle": "Technology Modernization",
                "subject": "Modernize Legacy Systems Fast",
                "body": "Hi Sarah,\n\nScaling AI from 5 to 50 use cases requires modern infrastructure.\n\nDevin accelerates legacy migrations and modernization projects 6-12x.\n\nCan we find time to connect this week?\n\nBest,\nJohn"
            },
            {
                "angle": "Financial Efficiency",
                "subject": "Cut Engineering Costs Dramatically",
                "body": "Hi Sarah,\n\nYour efficiency targets demand smart resource allocation.\n\nDevin delivers 6-12x efficiency gains on engineering tasks at Citi and Goldman.\n\nWould a quick call work next week?\n\nBest,\nJohn"
            },
            {
                "angle": "Customer Value & Growth",
                "subject": "Accelerate Customer Innovation Delivery",
                "body": "Hi Sarah,\n\nScaling AI use cases drives direct customer value.\n\nDevin frees engineering capacity so teams focus on customer innovation.\n\nOpen to connecting this week?\n\nBest,\nJohn"
            },
            {
                "angle": "Competitive Advantage",
                "subject": "Stay Ahead With AI Engineering",
                "body": "Hi Sarah,\n\nYour competitors are already deploying AI agents.\n\nDevin is in production at Citi and Goldman, delivering 6-12x gains.\n\nLet's find time to discuss next week?\n\nBest,\nJohn"
            }
        ]
    }


@pytest.mark.asyncio
async def test_generate_outreach_emails_cold_outreach():
    """Test cold outreach email generation returns 5 templates"""
    mock_response = _make_mock_templates()
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await generate_outreach_emails(
            message_type="cold_outreach",
            prospect_name="Sarah Johnson",
            prospect_title="Chief Technology Officer",
            prospect_company="Acme Corp",
            unique_fact="Named CIO of the Year finalist",
            business_initiative="Scaling AI use cases from 5 to 50",
            manager_name="John Smith"
        )
        
        # Verify result structure
        assert "templates" in result
        assert isinstance(result["templates"], list)
        assert len(result["templates"]) == 5
        assert "metadata" in result
        
        # Verify each template has required fields
        for template in result["templates"]:
            assert "angle" in template
            assert "subject" in template
            assert "body" in template
        
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
    """Test in-person ask email generation returns 5 templates"""
    mock_response = _make_mock_templates()
    
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
            meeting_purpose="Private executive dinner in Chicago on Oct 9th at 6pm at Elske"
        )
        
        assert "templates" in result
        assert len(result["templates"]) == 5
        assert result["metadata"]["message_type"] == "in_person_ask"


@pytest.mark.asyncio
async def test_generate_outreach_emails_executive_alignment():
    """Test executive alignment email generation returns 5 templates"""
    mock_response = _make_mock_templates()
    
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
        
        assert "templates" in result
        assert len(result["templates"]) == 5
        assert result["metadata"]["message_type"] == "executive_alignment"


@pytest.mark.asyncio
async def test_generate_outreach_emails_missing_templates():
    """Test error handling when model response missing templates array"""
    mock_response = {
        "subject": "Old format response",
        "body": "This is the old format"
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        with pytest.raises(ValueError, match="missing 'templates' array"):
            await generate_outreach_emails(
                message_type="cold_outreach",
                prospect_name="Test",
                prospect_title="Test",
                prospect_company="Test",
                unique_fact="Test",
                business_initiative="Test"
            )


@pytest.mark.asyncio
async def test_generate_outreach_emails_missing_subject_in_template():
    """Test error handling when a template is missing subject"""
    mock_response = {
        "templates": [
            {"angle": "Strategy & Digital Leadership", "body": "Email body without subject"}
        ]
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        with pytest.raises(ValueError, match="Template 0 missing 'subject' field"):
            await generate_outreach_emails(
                message_type="cold_outreach",
                prospect_name="Test",
                prospect_title="Test",
                prospect_company="Test",
                unique_fact="Test",
                business_initiative="Test"
            )


@pytest.mark.asyncio
async def test_generate_outreach_emails_missing_body_in_template():
    """Test error handling when a template is missing body"""
    mock_response = {
        "templates": [
            {"angle": "Strategy & Digital Leadership", "subject": "Test Subject"}
        ]
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        with pytest.raises(ValueError, match="Template 0 missing 'body' field"):
            await generate_outreach_emails(
                message_type="cold_outreach",
                prospect_name="Test",
                prospect_title="Test",
                prospect_company="Test",
                unique_fact="Test",
                business_initiative="Test"
            )


@pytest.mark.asyncio
async def test_generate_outreach_emails_missing_angle_in_template():
    """Test error handling when a template is missing angle"""
    mock_response = {
        "templates": [
            {"subject": "Test Subject", "body": "Test body"}
        ]
    }
    
    with patch('app.generator.generate_with_model', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        with pytest.raises(ValueError, match="Template 0 missing 'angle' field"):
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
    mock_response = _make_mock_templates()
    
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
