# Setup Guide

## Step-by-Step Installation

### 1. Navigate to Project
```bash
cd /Users/connorhaley/CascadeProjects/executive-note-gen
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key

**Option A: OpenAI (GPT-4o)**
```bash
cp .env.example .env
# Edit .env and add:
OPENAI_API_KEY=sk-your-actual-key-here
```

**Option B: Anthropic (Claude 3.5 Sonnet)**
```bash
cp .env.example .env
# Edit .env and add:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### 5. Run the Application

**Option A: Using run script**
```bash
./run.sh
```

**Option B: Manual start**
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open Browser
Navigate to: **http://localhost:8000**

## Testing

Run tests to verify setup:
```bash
pytest
```

## Quick Test

Once the server is running, test the API:

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Sarah Johnson",
    "prospect_title": "Chief Technology Officer",
    "prospect_company": "Acme Financial Services",
    "unique_fact": "Recently named CIO of the Year finalist",
    "business_initiative": "Scaling AI use cases from 5 to 50 by Q4",
    "manager_name": "John Smith",
    "model_provider": "openai"
  }'
```

## Troubleshooting

**Virtual environment not activated?**
```bash
source venv/bin/activate
```

**Port 8000 already in use?**
```bash
python3 -m uvicorn app.main:app --reload --port 8001
```

**API key not working?**
- Verify key is correct in `.env`
- Check key has proper permissions
- Ensure no extra spaces in `.env` file

**Import errors?**
```bash
pip install --upgrade -r requirements.txt
```

## Next Steps

1. **Set workspace**: In your IDE, set `/Users/connorhaley/CascadeProjects/executive-note-gen` as the active workspace
2. **Customize prompts**: Edit `app/prompts.py` to adjust messaging guidelines
3. **Add case studies**: Update the case study library in `app/prompts.py`
4. **Deploy**: Follow README.md deployment section for production deployment
