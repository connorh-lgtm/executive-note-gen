# Testing Guide

## Overview

The Ghost Note App now has comprehensive test coverage across all core modules. This document explains how to run tests and what is being tested.

## Test Suite Summary

**Total Tests: 28**
- **test_prompts.py**: 12 tests - Prompt building and message type validation
- **test_generator.py**: 6 tests - Email generation logic with mocked LLM calls
- **test_api.py**: 10 tests - FastAPI endpoint testing

## Running Tests

### Run All Tests
```bash
source venv/bin/activate
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_prompts.py -v
pytest tests/test_generator.py -v
pytest tests/test_api.py -v
```

### Run Single Test
```bash
pytest tests/test_prompts.py::test_build_prompt_cold_outreach -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Quick Test (No Verbose)
```bash
pytest tests/ -q
```

## Test Coverage by Module

### 1. Prompt Building (`test_prompts.py`)

Tests the `prompts_v2.py` module which builds system and user prompts for LLM generation.

**Tests:**
- ✅ `test_build_prompt_cold_outreach` - Cold outreach message type
- ✅ `test_build_prompt_in_person_ask` - In-person invitation with meeting purpose
- ✅ `test_build_prompt_executive_alignment` - Executive alignment with traction
- ✅ `test_build_prompt_default_manager` - Default manager name handling
- ✅ `test_build_prompt_first_name_extraction` - First name extraction logic
- ✅ `test_get_message_type_context_cold_outreach` - Cold outreach examples/instructions
- ✅ `test_get_message_type_context_in_person_ask` - In-person ask examples/instructions
- ✅ `test_get_message_type_context_executive_alignment` - Exec alignment examples/instructions
- ✅ `test_build_prompt_case_study_library` - Case study inclusion (Nubank, Citi, Goldman)
- ✅ `test_build_prompt_output_format` - JSON output format specification
- ✅ `test_build_prompt_constraints` - Word count and subject line constraints
- ✅ `test_build_prompt_all_message_types` - All three message types work without errors

**What's Tested:**
- Message type-specific prompt building
- First name extraction from full names
- Manager name personalization
- Meeting purpose inclusion for in-person asks
- Case study library presence
- Word count constraints (80-110 words)
- Subject line constraints (≤6 words)
- Citi/Goldman Sachs validation inclusion
- JSON output format specification

### 2. Email Generation (`test_generator.py`)

Tests the `generator.py` module with mocked LLM API calls.

**Tests:**
- ✅ `test_generate_outreach_emails_cold_outreach` - Cold outreach generation
- ✅ `test_generate_outreach_emails_in_person_ask` - In-person ask generation
- ✅ `test_generate_outreach_emails_executive_alignment` - Executive alignment generation
- ✅ `test_generate_outreach_emails_missing_subject` - Error handling for missing subject
- ✅ `test_generate_outreach_emails_missing_body` - Error handling for missing body
- ✅ `test_generate_outreach_emails_default_manager` - Default manager name

**What's Tested:**
- Email generation for all three message types
- Metadata inclusion (message_type, prospect_name, company, manager, provider)
- Error handling for malformed LLM responses
- Default parameter handling
- Model provider selection (OpenAI vs Anthropic)

### 3. API Endpoints (`test_api.py`)

Tests the FastAPI endpoints in `main.py` using TestClient.

**Tests:**
- ✅ `test_root_endpoint` - Root endpoint serves index.html
- ✅ `test_health_endpoint` - Health check returns correct status
- ✅ `test_generate_endpoint_success` - Successful email generation
- ✅ `test_generate_endpoint_missing_fields` - Validation error for missing fields
- ✅ `test_generate_endpoint_invalid_message_type` - Invalid message type handling
- ✅ `test_generate_endpoint_with_meeting_purpose` - Meeting purpose parameter
- ✅ `test_feedback_endpoint_success` - Feedback submission
- ✅ `test_feedback_endpoint_missing_fields` - Feedback validation
- ✅ `test_enrich_endpoint_success` - LinkedIn enrichment
- ✅ `test_summarize_bio_endpoint_fallback` - Fallback for missing data

**What's Tested:**
- HTTP status codes
- Request/response JSON structure
- Input validation (Pydantic models)
- Error handling
- Feedback storage
- LinkedIn enrichment integration
- Legacy endpoint compatibility

## Test Architecture

### Mocking Strategy

Tests use `unittest.mock` to avoid making real API calls:

```python
from unittest.mock import AsyncMock, patch

@patch('app.generator.generate_with_model', new_callable=AsyncMock)
async def test_example(mock_generate):
    mock_generate.return_value = {"subject": "Test", "body": "Test"}
    # Test code here
```

### Async Testing

Async tests use `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### FastAPI Testing

API tests use `TestClient` for synchronous testing:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.post("/api/generate", json={...})
assert response.status_code == 200
```

## What's NOT Tested

The following areas still need test coverage:

1. **model_client.py** - LLM API integration (OpenAI, Anthropic, Perplexity)
2. **linkedin_enrichment.py** - Perplexity API integration
3. **sender_profiles.py** - Sender context building
4. **Frontend JavaScript** - UI interactions and form validation
5. **Integration tests** - End-to-end workflows with real APIs
6. **Performance tests** - Load testing and response times
7. **Security tests** - Input sanitization, injection attacks

## Adding New Tests

### 1. Create Test File

```python
"""
Test description
"""
import pytest
from app.your_module import your_function


def test_your_feature():
    """Test description"""
    result = your_function()
    assert result == expected_value
```

### 2. Run Tests

```bash
pytest tests/test_your_module.py -v
```

### 3. Update This Document

Add your new tests to the appropriate section above.

## Continuous Integration

To set up CI/CD, add this GitHub Actions workflow:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

## Troubleshooting

### Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

### Async Test Warnings

Add to `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

### Test Discovery Issues

Ensure all test files:
- Start with `test_`
- Are in the `tests/` directory
- Have `__init__.py` in the tests directory

## Best Practices

1. **One assertion per test** - Makes failures easier to debug
2. **Descriptive test names** - `test_generate_cold_outreach_with_valid_input`
3. **Mock external dependencies** - Don't make real API calls in tests
4. **Test edge cases** - Empty strings, None values, invalid inputs
5. **Keep tests fast** - Use mocks, avoid sleep(), minimize I/O
6. **Test behavior, not implementation** - Focus on what, not how

## Next Steps

1. Add integration tests with real API calls (separate test suite)
2. Add frontend tests with Playwright or Cypress
3. Set up code coverage reporting (aim for >80%)
4. Add performance/load tests
5. Implement security testing (OWASP Top 10)
6. Add mutation testing to verify test quality

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
