# Testing Account Knowledge in executive-note-gen

## Architecture
Account knowledge flows through a pipeline:
1. **Markdown files** in `accounts/` (one per company) with structured sections: Overview, Situation (focus, challenges, recent_activity), Key Initiatives, Positioning (focus, competitive, differentiators), Team Contacts, Contact Notes
2. **Parser** (`app/account_knowledge.py`) reads markdown → structured dicts
3. **Prompt builder** (`app/prompts_v2.py` → `build_prompt()`) calls `format_account_context_for_prompt()` → injects `[ACCOUNT KNOWLEDGE]` section into system prompt
4. **LLM** generates emails using the enriched prompt

## Key Functions for Testing
```python
from app.account_knowledge import list_known_accounts, get_account_context, format_account_context_for_prompt
from app.prompts_v2 import build_prompt

# List all recognized accounts
accounts = list_known_accounts()  # Returns list of uppercase company names

# Get structured context for a company
ctx = get_account_context('Kroger')  # Returns dict with situation, key_initiatives, positioning, status, etc.

# Get formatted prompt string
prompt_str = format_account_context_for_prompt('Kroger', 'John Smith')

# Full prompt build (includes account knowledge in system prompt)
system_prompt, user_prompt = build_prompt(
    message_type='cold_outreach',
    prospect_name='John Smith',
    prospect_title='CTO',
    prospect_company='Kroger',
    unique_fact='Led digital transformation',
    business_initiative='AI personalization',
    manager_name='Test Manager'
)
```

## Testing Without LLM API Keys
The app requires an OpenAI/Anthropic/Perplexity API key in `.env` to generate emails. If no key is available:
- You can still verify the full data pipeline (markdown → parser → prompt builder) using the Python functions above
- The server will start with a placeholder key for health/UI checks, but `/api/generate` will fail
- Create a temporary `.env` with `OPENAI_API_KEY=sk-test-placeholder` to start the server for health checks, then clean it up

## Recommended Test Cases for Account Data Changes
1. **All accounts recognized**: `len(list_known_accounts())` matches expected count
2. **Fields populated**: For each account, verify `situation.focus`, `situation.challenges`, `key_initiatives`, `positioning.focus`, and `status` are non-empty
3. **Cross-company contamination**: Spot-check unique data points are in the correct account (e.g., Kroger→"agentic shopping", Wayfair→"Advanced" status)
4. **Prompt integration**: Call `build_prompt()` with a known company → verify `[ACCOUNT KNOWLEDGE]` and `COMPANY CONTEXT (CompanyName)` appear in system prompt
5. **Unknown company handling**: Call `build_prompt()` with a fake company → verify NO `[ACCOUNT KNOWLEDGE]` section
6. **Server health**: Start server, hit `/health` endpoint → expect `{"status":"healthy"}`

## Notes
- The `## Research Intelligence` section in account files is NOT parsed by `account_knowledge.py` — it's human-readable reference only
- Only standard sections (Overview, Situation, Key Initiatives, Positioning, Team Contacts, Contact Notes) flow into prompts
- Unit tests: `pytest tests/ -v` (31 tests covering parser functionality)
- Server startup: `python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Devin Secrets Needed
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` or `PERPLEXITY_API_KEY` — required for full email generation testing (stored in `.env` file)
