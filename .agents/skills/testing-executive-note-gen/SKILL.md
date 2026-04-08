# Testing Executive Note Generator

How to test the executive-note-gen application locally.

## Prerequisites

- Python 3.9+ with dependencies installed (`pip install -r requirements.txt`)
- Optional: `ANTHROPIC_API_KEY` environment variable for real LLM generation

## Devin Secrets Needed

- `ANTHROPIC_API_KEY` — Required for real end-to-end LLM generation testing. Without it, you can still test the frontend UI by injecting mock data.

## Running the App

```bash
cd /home/ubuntu/repos/executive-note-gen
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check: `curl http://localhost:8000/health`

The app serves at `http://localhost:8000` with the frontend at the root path.

## Running Tests

```bash
cd /home/ubuntu/repos/executive-note-gen
python -m pytest tests/ -v
```

All tests use mocked LLM calls and do not require an API key.

## Testing the Frontend UI Without an API Key

If no `ANTHROPIC_API_KEY` is available, you can test the frontend by injecting mock data via Playwright CDP:

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:29229')
        page = browser.contexts[0].pages[0]
        await page.goto('http://localhost:8000')
        await page.wait_for_load_state('networkidle')
        
        result = await page.evaluate("""() => {
            const mockResult = {
                templates: [
                    { angle: "Strategy & Digital Leadership", subject: "Test Subject 1", body: "Test body 1" },
                    { angle: "Technology Modernization", subject: "Test Subject 2", body: "Test body 2" },
                    { angle: "Financial Efficiency", subject: "Test Subject 3", body: "Test body 3" },
                    { angle: "Customer Value & Growth", subject: "Test Subject 4", body: "Test body 4" },
                    { angle: "Competitive Advantage", subject: "Test Subject 5", body: "Test body 5" }
                ],
                metadata: { message_type: "cold_outreach", prospect_name: "Test", prospect_company: "TestCo", manager_name: "Manager", model_provider: "anthropic" }
            };
            displayEmail(mockResult);
            const tabs = document.querySelectorAll('#templateTabs button');
            return { tabCount: tabs.length };
        }""")
        print(f"Tabs rendered: {result['tabCount']}")

asyncio.run(main())
```

This calls `displayEmail()` directly to render the tabbed UI with mock data.

## Testing Rate Limiting

Restart the server with a low rate limit to test quickly:

```bash
GENERATE_RATE_LIMIT="2/minute" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then send rapid requests:
```bash
# These will return 400 (no API key) but consume rate limit slots
curl -X POST http://localhost:8000/api/generate -H "Content-Type: application/json" \
  -d '{"prospect_name":"Test","prospect_title":"CTO","prospect_company":"Acme","unique_fact":"Award","business_initiative":"AI","message_type":"cold_outreach"}'
# Repeat until you get HTTP 429
```

Rate limit env vars: `GENERATE_RATE_LIMIT` (default 10/minute), `ENRICH_RATE_LIMIT` (default 20/minute), `FEEDBACK_RATE_LIMIT` (default 30/minute).

## Form Field IDs

The HTML form fields have these IDs (useful for Playwright automation):
- `prospect_name` — Prospect name input
- `message_type` — Message type select dropdown (values: `cold_outreach`, `in_person_ask`, `executive_alignment`)
- `prospect_title` — Title input
- `prospect_company` — Company input
- `unique_fact` — Unique fact textarea
- `business_initiative` — Business initiative textarea
- `manager_name` — Sender name input (optional)
- `meeting_purpose` — Meeting purpose textarea (shown for in-person ask type)

## Key Frontend Functions

- `displayEmail(result)` — Renders the tabbed UI from a result object with `templates` array
- `showTemplate(index)` — Switches to a specific template tab
- `copyEmail()` — Copies the currently visible template to clipboard
- `saveToHistory(result)` — Saves result to localStorage
- `loadHistoryItem(index)` — Loads a history item and displays it

## Known Issues

- Clipboard read via Playwright may hang due to browser permission prompts. The copy button visual feedback (checkmark icon) can be used as confirmation instead.
- Clicking a history item re-saves it, potentially creating duplicate entries in the sidebar.
- Old localStorage history entries (pre-templates format with top-level `subject`/`body`) will not load correctly in the new tabbed UI. Consider clearing localStorage if testing after upgrading.
