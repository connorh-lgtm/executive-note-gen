# Testing Executive Note Gen

## Devin Secrets Needed
- `ANTHROPIC_API_KEY` — required for full email generation testing (UI → API → Anthropic → response). Without it, only the data layer and unit tests can be verified.

## Running the Test Suite

```bash
cd /home/ubuntu/repos/executive-note-gen
python -m pytest tests/ -v
```

Expected: 27/28 pass. `test_enrich_endpoint_success` may fail — this is a pre-existing issue unrelated to most changes.

## Testing the Account Knowledge Markdown Parser

The account knowledge system reads `.md` files from `accounts/` and parses them into dicts. To verify parsing:

```python
import sys
sys.path.insert(0, '.')
from app.account_knowledge import _parse_account_markdown
account = _parse_account_markdown('accounts/Kroger.md')
# Check: account["company_name"], account["industry"], account["situation"], etc.
```

Key fields to validate: `company_name`, `industry`, `status`, `situation` (focus, challenges, recent_activity), `team_contacts`, `key_initiatives`, `positioning` (focus, differentiators, competitive), `contact_notes`.

## Testing Cache Invalidation

The cache uses a `None` sentinel (not `{}`) to distinguish "never loaded" from "loaded but empty". To test:

```python
import app.account_knowledge as ak
# Reset cache
ak._cached_accounts = None
ak._cached_file_count = 0
ak._cache_load_time = 0.0
ak.ACCOUNTS_DIR = '/path/to/temp/dir'

# Call _get_accounts() twice and verify _cache_load_time is stable
```

Things to verify:
- Empty directory: cache is set after first call, not rescanned on second
- Deleted file: removing a `.md` file triggers reload (account disappears)
- Malformed file: an empty/broken `.md` doesn't cause cache thrashing (uses `_cached_file_count` to track files found on disk vs successfully parsed)

## Testing the Model Client

`generate_with_model` is **async** — must use `asyncio.run()` or `await` when testing:

```python
import asyncio
from unittest.mock import patch, AsyncMock

async def test():
    with patch('app.model_client.call_anthropic', new_callable=AsyncMock) as mock:
        mock.return_value = '{"subject": "Test", "body": "Hello"}'
        from app.model_client import generate_with_model
        result = await generate_with_model("System", "User", provider="openai")
        assert mock.called  # Routes to Anthropic regardless of provider param

asyncio.run(test())
```

`call_openai` and `call_perplexity` were removed from `model_client.py`. The Perplexity client in `linkedin_enrichment.py` is separate and still exists.

## Testing the Full UI Flow

Requires `ANTHROPIC_API_KEY` set in environment. Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000` in browser. Fill in the form with a known company (e.g., "Kroger") to verify account knowledge is injected into the generated email.

## Public API Verification

```python
from app.account_knowledge import format_account_context_for_prompt
output = format_account_context_for_prompt("Kroger")
# Should contain: "COMPANY CONTEXT (Kroger):" when account data is populated
```

## Notes
- Bullet parsing uses `removeprefix('- ')` (not `lstrip('- ')`) to avoid stripping leading dashes from values like `"-20% cost reduction"`
- Account files live in `accounts/` — changes are auto-detected via mtime checking (no restart needed)
- `TEMPLATE.md` is excluded from parsing
