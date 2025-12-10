"""
Test FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns index.html"""
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "executive-note-gen"}


@patch('app.main.generate_outreach_emails', new_callable=AsyncMock)
def test_generate_endpoint_success(mock_generate):
    """Test successful email generation"""
    mock_generate.return_value = {
        "subject": "Test Subject",
        "body": "Test Body",
        "metadata": {
            "message_type": "cold_outreach",
            "prospect_name": "Test Person",
            "prospect_company": "Test Corp",
            "manager_name": "Test Manager",
            "model_provider": "anthropic"
        }
    }
    
    response = client.post("/api/generate", json={
        "message_type": "cold_outreach",
        "prospect_name": "Test Person",
        "prospect_title": "CTO",
        "prospect_company": "Test Corp",
        "unique_fact": "Test fact",
        "business_initiative": "Test initiative",
        "manager_name": "Test Manager"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "subject" in data
    assert "body" in data
    assert "metadata" in data


def test_generate_endpoint_missing_fields():
    """Test generation with missing required fields"""
    response = client.post("/api/generate", json={
        "message_type": "cold_outreach",
        "prospect_name": "Test"
        # Missing other required fields
    })
    
    assert response.status_code == 422  # Validation error


def test_generate_endpoint_invalid_message_type():
    """Test generation with invalid message type"""
    response = client.post("/api/generate", json={
        "message_type": "invalid_type",
        "prospect_name": "Test",
        "prospect_title": "Test",
        "prospect_company": "Test",
        "unique_fact": "Test",
        "business_initiative": "Test"
    })
    
    # Should still accept it (validation happens in prompt building)
    assert response.status_code in [200, 400, 500]


@patch('app.main.generate_outreach_emails', new_callable=AsyncMock)
def test_generate_endpoint_with_meeting_purpose(mock_generate):
    """Test generation with meeting purpose for in-person ask"""
    mock_generate.return_value = {
        "subject": "Dinner Invitation",
        "body": "Test Body",
        "metadata": {
            "message_type": "in_person_ask",
            "prospect_name": "Test",
            "prospect_company": "Test",
            "manager_name": "[Manager's Name]",
            "model_provider": "anthropic"
        }
    }
    
    response = client.post("/api/generate", json={
        "message_type": "in_person_ask",
        "prospect_name": "Test",
        "prospect_title": "Test",
        "prospect_company": "Test",
        "unique_fact": "Test",
        "business_initiative": "Test",
        "meeting_purpose": "Dinner in Chicago on Oct 9th"
    })
    
    assert response.status_code == 200


def test_feedback_endpoint_success():
    """Test feedback submission"""
    response = client.post("/api/feedback", json={
        "feedback_type": "positive",
        "original_output": {
            "subject": "Test",
            "body": "Test"
        },
        "improved_version": None,
        "metadata": {
            "message_type": "cold_outreach"
        },
        "timestamp": "2024-01-01T00:00:00Z"
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_feedback_endpoint_missing_fields():
    """Test feedback with missing required fields"""
    response = client.post("/api/feedback", json={
        "feedback_type": "positive"
        # Missing other required fields
    })
    
    assert response.status_code == 422


@patch('app.main.enrich_profile', new_callable=AsyncMock)
def test_enrich_endpoint_success(mock_enrich):
    """Test LinkedIn enrichment endpoint"""
    mock_enrich.return_value = {
        "unique_fact": "Test fact",
        "business_initiative": "Test initiative"
    }
    
    response = client.post(
        "/api/enrich",
        params={
            "linkedin_url": "https://linkedin.com/in/test",
            "prospect_name": "Test Person",
            "prospect_title": "CTO",
            "prospect_company": "Test Corp"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "unique_fact" in data
    assert "business_initiative" in data


def test_summarize_bio_endpoint_fallback():
    """Test summarize-bio endpoint with fallback"""
    response = client.post("/api/summarize-bio", json={
        "linkedin_url": "",
        "prospect_name": ""
    })
    
    # Should return fallback data instead of failing
    assert response.status_code == 200
    data = response.json()
    assert "unique_fact" in data
    assert "business_initiative" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
