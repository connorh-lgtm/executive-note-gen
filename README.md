# Executive Note Generator

A production-ready web application that generates high-caliber executive outreach emails using **Mega-Prompt v13**. Built for crafting Fortune 50 EVP-level communications to enterprise executives (CIO, CTO, CDO, Head of Engineering).

## Features

- **5 Strategic Angles**: Generates 5 distinct email templates per prospect
  - Strategy & Digital Leadership
  - Technology Modernization
  - Financial Efficiency
  - Customer Value & Growth
  - Competitive Advantage

- **Mega-Prompt v13 Engine**: Embedded prompt engineering framework with:
  - Board-level tone and structure
  - Case study library (Nubank, Goldman Sachs, Ramp, etc.)
  - Global FS validation paragraph
  - 120-150 word constraint
  - Executive-caliber CTAs

- **Multi-Provider Support**: OpenAI (GPT-4o) and Anthropic (Claude 3.5 Sonnet)

- **Modern UI**: Clean, responsive landing page with real-time generation

## Quick Start

### 1. Prerequisites

- Python 3.9+
- OpenAI API key OR Anthropic API key

### 2. Installation

```bash
cd /Users/connorhaley/CascadeProjects/executive-note-gen
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 4. Run

```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open browser to: **http://localhost:8000**

## API Usage

### POST /api/generate

Generate 5 email templates.

**Request:**
```json
{
  "prospect_name": "Sarah Johnson",
  "prospect_title": "Chief Technology Officer",
  "prospect_company": "Acme Financial Services",
  "unique_fact": "Recently named CIO of the Year finalist",
  "business_initiative": "Scaling AI use cases from 5 to 50 by Q4",
  "manager_name": "John Smith",
  "model_provider": "openai"
}
```

**Response:**
```json
{
  "templates": [
    {
      "angle": "Strategy & Digital Leadership",
      "subject": "AI Scale & Strategic Velocity",
      "body": "Hi Sarah,..."
    }
  ],
  "metadata": {
    "prospect_name": "Sarah Johnson",
    "prospect_company": "Acme Financial Services",
    "manager_name": "John Smith",
    "model_provider": "openai"
  }
}
```

## Mega-Prompt v13 Details

The application uses a carefully structured prompt that ensures:

- **Role**: Fortune 50 EVP writing to enterprise executives
- **Structure**: Hook → Business Case → Devin Value → Case Study → FS Validation → CTA
- **Constraints**: 120-150 words, ≤6 word subjects, boardroom tone
- **Case Studies**: Rotates through Nubank, Bilt, Gumroad, Ramp, Linktree, Crossmint, Goldman Sachs
- **Validation**: Always includes Citi/Goldman Sachs production deployment proof
- **Personalization**: Optional manager background (Medallia, global experience, etc.)

## Development

### Project Structure

```
app/
├── main.py              # FastAPI application
├── generator.py         # Core generation logic
├── prompts.py           # Mega-Prompt v13 template
└── model_client.py      # OpenAI/Anthropic abstraction
static/
└── index.html           # Landing page UI
```

### Adding New Case Studies

Edit `app/prompts.py` and add to the `CASE STUDY LIBRARY` section in `MEGA_PROMPT_SYSTEM`.

### Customizing Prompt

Modify `MEGA_PROMPT_SYSTEM` in `app/prompts.py` to adjust:
- Word count constraints
- Tone and style
- Required sections
- CTA options

## Deployment

### Local

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Production (Render, Fly.io, Railway)

1. Set environment variables in platform dashboard
2. Use `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Ensure `requirements.txt` is present

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

**API Key Error**: Ensure `.env` file exists and contains valid API key

**Import Error**: Activate virtual environment: `source venv/bin/activate`

**Port in Use**: Change port: `uvicorn app.main:app --port 8001`

**Model Response Error**: Check API key permissions and rate limits

## License

Proprietary - Internal Use Only
