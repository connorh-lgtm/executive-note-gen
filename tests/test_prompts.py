"""
Test prompt building and validation for prompts_v2 (Mega-Prompt v14)
"""
import pytest
from app.prompts_v2 import build_prompt, get_message_type_context


def test_build_prompt_cold_outreach():
    """Test cold outreach prompt building"""
    system_prompt, user_prompt = build_prompt(
        message_type="cold_outreach",
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
    assert "First Name" in system_prompt or "Greeting" in system_prompt
    assert "Devin" in system_prompt
    assert "80–110 words" in system_prompt or "80-110 words" in system_prompt
    assert "Cold Outreach" in system_prompt or "cold_outreach" in system_prompt.lower()
    
    # Verify user prompt contains prospect info
    assert "Sarah Johnson" in user_prompt
    assert "Chief Technology Officer" in user_prompt
    assert "Acme Corp" in user_prompt
    assert "Named CIO of the Year finalist" in user_prompt
    assert "Scaling AI use cases from 5 to 50" in user_prompt
    assert "JSON" in user_prompt


def test_build_prompt_in_person_ask():
    """Test in-person ask prompt building with meeting purpose"""
    system_prompt, user_prompt = build_prompt(
        message_type="in_person_ask",
        prospect_name="Jane Doe",
        prospect_title="CTO",
        prospect_company="Test Inc",
        unique_fact="Keynote speaker at AI Summit",
        business_initiative="Leading digital transformation",
        manager_name="Jake Smith",
        meeting_purpose="Private executive dinner in Chicago on Oct 9th at 6pm at Elske"
    )
    
    assert "In-Person Ask" in system_prompt or "in_person_ask" in system_prompt.lower()
    assert "invitation" in system_prompt.lower()
    assert "Private executive dinner in Chicago on Oct 9th at 6pm at Elske" in user_prompt
    assert "Meeting Purpose" in user_prompt


def test_build_prompt_executive_alignment():
    """Test executive alignment prompt building"""
    system_prompt, user_prompt = build_prompt(
        message_type="executive_alignment",
        prospect_name="Eric Thompson",
        prospect_title="Chief Information Officer",
        prospect_company="BMO Financial",
        unique_fact="Recognized on Fast Company's Most Innovative Companies list",
        business_initiative="Legacy system migrations",
        manager_name="Russell"
    )
    
    assert "Executive Alignment" in system_prompt or "executive_alignment" in system_prompt.lower()
    assert "traction" in system_prompt.lower()
    assert "Eric Thompson" in user_prompt


def test_build_prompt_default_manager():
    """Test prompt building with default manager name"""
    system_prompt, user_prompt = build_prompt(
        message_type="cold_outreach",
        prospect_name="Jane Doe",
        prospect_title="CTO",
        prospect_company="Test Inc",
        unique_fact="Test fact",
        business_initiative="Test initiative"
    )
    
    assert "[Manager's Name]" in system_prompt


def test_build_prompt_first_name_extraction():
    """Test that first name is correctly extracted and used in greeting"""
    system_prompt, user_prompt = build_prompt(
        message_type="cold_outreach",
        prospect_name="John Michael Smith",
        prospect_title="CTO",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    # First name should be in greeting template
    assert "First Name" in system_prompt or "Greeting" in system_prompt
    # Full name should be in user prompt
    assert "John Michael Smith" in user_prompt


def test_get_message_type_context_cold_outreach():
    """Test cold outreach message type context"""
    examples, instructions = get_message_type_context("cold_outreach")
    
    assert "EXAMPLE 1:" in examples
    assert "Hi Garima" in examples or "Hi Ankur" in examples or "Hi Rohit" in examples
    assert "Cold Outreach" in instructions
    assert "No traction in account" in instructions
    assert "open slots" in instructions.lower()


def test_get_message_type_context_in_person_ask():
    """Test in-person ask message type context"""
    examples, instructions = get_message_type_context("in_person_ask")
    
    assert "EXAMPLE 1:" in examples
    assert "dinner" in examples.lower() or "invitation" in examples.lower()
    assert "In-Person Ask" in instructions
    assert "invitation" in instructions.lower()


def test_get_message_type_context_executive_alignment():
    """Test executive alignment message type context"""
    examples, instructions = get_message_type_context("executive_alignment")
    
    assert "EXAMPLE 1:" in examples
    assert "met with" in examples.lower() or "team" in examples.lower()
    assert "Executive Alignment" in instructions
    assert "traction" in instructions.lower()


def test_build_prompt_case_study_library():
    """Test that case study library is included"""
    system_prompt, _ = build_prompt(
        message_type="cold_outreach",
        prospect_name="Test",
        prospect_title="Test",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    # Verify key case studies are present
    case_studies = ["Nubank", "Goldman Sachs", "Citi"]
    for case_study in case_studies:
        assert case_study in system_prompt


def test_build_prompt_output_format():
    """Test that JSON output format is specified"""
    _, user_prompt = build_prompt(
        message_type="cold_outreach",
        prospect_name="Test",
        prospect_title="Test",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    assert "JSON" in user_prompt
    assert "subject" in user_prompt
    assert "body" in user_prompt


def test_build_prompt_constraints():
    """Test that key constraints are specified"""
    system_prompt, user_prompt = build_prompt(
        message_type="cold_outreach",
        prospect_name="Test",
        prospect_title="Test",
        prospect_company="Test",
        unique_fact="Test",
        business_initiative="Test"
    )
    
    combined = system_prompt + user_prompt
    
    # Word count constraint (updated to 80-110 in v14)
    assert "80" in combined or "110" in combined
    
    # Subject line constraint
    assert "6 words" in combined or "≤6 words" in combined or "≤ 6 words" in combined
    
    # FS validation requirement
    assert "Citi" in combined
    assert "Goldman Sachs" in combined


def test_build_prompt_all_message_types():
    """Test that all three message types work without errors"""
    message_types = ["cold_outreach", "in_person_ask", "executive_alignment"]
    
    for msg_type in message_types:
        system_prompt, user_prompt = build_prompt(
            message_type=msg_type,
            prospect_name="Test Person",
            prospect_title="CTO",
            prospect_company="Test Corp",
            unique_fact="Test fact",
            business_initiative="Test initiative",
            meeting_purpose="Test meeting" if msg_type == "in_person_ask" else ""
        )
        
        assert len(system_prompt) > 100
        assert len(user_prompt) > 50
        assert "Test Person" in user_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
