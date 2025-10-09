"""
Test prompt building and validation
"""
import pytest
from app.prompts import build_prompt


def test_build_prompt_basic():
    """Test basic prompt building"""
    system_prompt, user_prompt = build_prompt(
        prospect_name="Sarah Johnson",
        prospect_title="Chief Technology Officer",
        prospect_company="Acme Corp",
        unique_fact="Named CIO of the Year finalist",
        business_initiative="Scaling AI use cases from 5 to 50",
        manager_name="John Smith"
    )
    
    # Verify system prompt contains key elements
    assert "Fortune 50 EVP" in system_prompt
    assert "John Smith" in system_prompt
    assert "Sarah" in system_prompt  # First name extracted
    assert "Devin" in system_prompt
    assert "120–150 words" in system_prompt
    
    # Verify user prompt contains prospect info
    assert "Sarah Johnson" in user_prompt
    assert "Chief Technology Officer" in user_prompt
    assert "Acme Corp" in user_prompt
    assert "Named CIO of the Year finalist" in user_prompt
    assert "Scaling AI use cases from 5 to 50" in user_prompt


def test_build_prompt_default_manager():
    """Test prompt building with default manager name"""
    system_prompt, user_prompt = build_prompt(
        prospect_name="Jane Doe",
        prospect_title="CTO",
        prospect_company="Test Inc",
        unique_fact="Test fact",
        business_initiative="Test initiative"
    )
    
    assert "[Manager's Name]" in system_prompt


def test_build_prompt_first_name_extraction():
    """Test that first name is correctly extracted"""
    system_prompt, _ = build_prompt(
        prospect_name="John Michael Smith",
        prospect_title="CTO",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    assert "John" in system_prompt


def test_build_prompt_case_study_library():
    """Test that case study library is included"""
    system_prompt, _ = build_prompt(
        prospect_name="Test",
        prospect_title="Test",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    # Verify all case studies are present
    case_studies = ["Nubank", "Bilt", "Gumroad", "Ramp", "Linktree", "Crossmint", "Goldman Sachs"]
    for case_study in case_studies:
        assert case_study in system_prompt


def test_build_prompt_strategic_angles():
    """Test that all 5 strategic angles are specified"""
    system_prompt, user_prompt = build_prompt(
        prospect_name="Test",
        prospect_title="Test",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    angles = [
        "Strategy & Digital Leadership",
        "Technology Modernization",
        "Financial Efficiency",
        "Customer Value & Growth",
        "Competitive Advantage"
    ]
    
    for angle in angles:
        assert angle in system_prompt or angle in user_prompt


def test_build_prompt_output_format():
    """Test that JSON output format is specified"""
    _, user_prompt = build_prompt(
        prospect_name="Test",
        prospect_title="Test",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    assert "JSON" in user_prompt
    assert "templates" in user_prompt
    assert "angle" in user_prompt
    assert "subject" in user_prompt
    assert "body" in user_prompt


def test_build_prompt_constraints():
    """Test that key constraints are specified"""
    system_prompt, user_prompt = build_prompt(
        prospect_name="Test",
        prospect_title="Test",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    combined = system_prompt + user_prompt
    
    # Word count constraint
    assert "120" in combined and "150" in combined
    
    # Subject line constraint
    assert "6 words" in combined or "≤6 words" in combined or "≤ 6 words" in combined
    
    # FS validation requirement
    assert "Citi" in combined
    assert "Goldman Sachs" in combined


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
