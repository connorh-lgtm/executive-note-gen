# Prospect Research Feature - API Comparison

## Quick Reference

### Perplexity API
- **Website**: https://www.perplexity.ai/hub/api
- **Pricing**: https://docs.perplexity.ai/guides/pricing
- **Docs**: https://docs.perplexity.ai/
- **Free Tier**: $5 credit on signup
- **Models with Web Search**: 
  - `llama-3.1-sonar-small-128k-online` (cheapest)
  - `llama-3.1-sonar-large-128k-online` (better quality)
  - `llama-3.1-sonar-huge-128k-online` (best quality)

### Tavily API
- **Website**: https://tavily.com/
- **Pricing**: $0.001 per search
- **Docs**: https://docs.tavily.com/
- **Free Tier**: 1,000 searches/month
- **Best for**: AI agents, content extraction

---

## Perplexity Pricing

### Sonar Models (with web search)
- **sonar-small**: $0.20 per 1M tokens (input + output)
- **sonar-large**: $1.00 per 1M tokens
- **sonar-huge**: $5.00 per 1M tokens

### Cost per Research (estimated)
- Input: ~500 tokens (query)
- Output: ~1000 tokens (findings with citations)
- **Total**: ~1500 tokens = **$0.0003** (sonar-small)

**Much cheaper than I initially thought!**

---

## Tavily + Claude Pricing

### Combined Cost
- **Tavily**: 5 searches x $0.001 = $0.005
- **Claude**: ~2500 tokens x $0.003/1K = $0.0075
- **Total**: **$0.0125** per research

---

## Cost Comparison

| Approach | Cost per Research | Monthly (100 researches) |
|----------|------------------|--------------------------|
| **Perplexity (sonar-small)** | $0.0003 | $0.03 |
| **Perplexity (sonar-large)** | $0.0015 | $0.15 |
| **Claude + Tavily** | $0.0125 | $1.25 |

**Winner: Perplexity is 40x cheaper!** 🎉

---

## Sample Perplexity Code

### Basic Setup
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)

response = await client.chat.completions.create(
    model="llama-3.1-sonar-small-128k-online",
    messages=[
        {
            "role": "system",
            "content": "You are a research assistant."
        },
        {
            "role": "user",
            "content": "Research Sarah Johnson, CTO at Acme Corp"
        }
    ]
)

print(response.choices[0].message.content)
# Includes citations automatically!
```

### With Citations
```python
# Perplexity returns citations in the response
response = await client.chat.completions.create(
    model="llama-3.1-sonar-small-128k-online",
    messages=[...],
    return_citations=True  # Optional, enabled by default
)

# Access citations
content = response.choices[0].message.content
citations = response.citations  # List of URLs used
```

---

## Sample Tavily Code

### Basic Setup
```python
from tavily import TavilyClient

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

response = client.search(
    query="Sarah Johnson CTO Acme Corp AI blog",
    search_depth="advanced",
    max_results=5
)

# Returns: [{"title": "...", "url": "...", "content": "...", "score": 0.9}]
```

---

## Recommendation Update

Given the pricing discovery:

### **Perplexity is now the clear winner** 🏆

**Reasons**:
1. **40x cheaper** ($0.0003 vs $0.0125)
2. **Simpler** (one API vs two)
3. **Built-in citations**
4. **Real-time web search**
5. **Good quality** (Llama 3.1 is solid)

**Only downside**: Slightly less control over search queries

---

## Implementation Plan (Perplexity)

### Step 1: Get API Key
1. Sign up at https://www.perplexity.ai/
2. Go to API settings
3. Generate API key
4. Add to `.env`: `PERPLEXITY_API_KEY=pplx-xxx`

### Step 2: Install Package
```bash
pip install openai  # Perplexity uses OpenAI SDK
```

### Step 3: Create Research Module
```python
# app/researcher.py

from openai import AsyncOpenAI
import os

perplexity_client = AsyncOpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)

async def research_prospect(
    name: str,
    title: str,
    company: str
) -> dict:
    """
    Research prospect using Perplexity API
    
    Returns:
        {
            "findings": [
                {
                    "fact": "...",
                    "source": "...",
                    "url": "..."
                }
            ],
            "raw_response": "...",
            "citations": [...]
        }
    """
    
    prompt = f"""
    Research {name}, {title} at {company}.
    
    Find 2-3 compelling unique facts about them suitable for executive outreach:
    - Blog posts or articles they have written about AI, technology, or digital transformation
    - Speaking engagements, conferences, or presentations
    - Awards, recognition, or industry accolades
    - Major company initiatives or projects they have led
    - Quotes or interviews in major publications
    
    For each fact, provide:
    1. A concise, compelling statement (1-2 sentences)
    2. The source and date if available
    
    Focus on recent content (last 2-3 years) and AI/technology topics.
    Return facts that would make great hooks for personalized emails.
    """
    
    response = await perplexity_client.chat.completions.create(
        model="llama-3.1-sonar-small-128k-online",
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant specializing in finding compelling facts about executives for business outreach. Focus on AI, technology, and digital transformation topics."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,  # Lower for more factual responses
        max_tokens=1500
    )
    
    content = response.choices[0].message.content
    
    # Parse response and extract facts
    findings = parse_research_response(content)
    
    return {
        "findings": findings,
        "raw_response": content,
        "citations": getattr(response, 'citations', [])
    }


def parse_research_response(content: str) -> list:
    """Parse Perplexity response into structured findings"""
    # Implementation depends on response format
    # Perplexity usually returns well-structured text
    pass
```

### Step 4: Add API Endpoint
```python
# app/main.py

from app.researcher import research_prospect

class ResearchRequest(BaseModel):
    name: str
    title: str
    company: str
    linkedin_url: Optional[str] = None

@app.post("/api/research-prospect")
async def research_prospect_endpoint(request: ResearchRequest):
    """Research a prospect for unique facts"""
    try:
        results = await research_prospect(
            name=request.name,
            title=request.title,
            company=request.company
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing Strategy

### Test Cases
1. **Well-known exec** (e.g., "Satya Nadella, CEO, Microsoft")
   - Should find lots of content
   - Verify citation quality

2. **Mid-level exec** (e.g., "VP Engineering at mid-size company")
   - More challenging
   - Test fallback behavior

3. **Obscure person**
   - Should gracefully handle no results
   - Don't hallucinate

### Quality Metrics
- Fact relevance (AI/tech focus)
- Citation validity (real URLs)
- Recency (prefer last 2-3 years)
- Uniqueness (not generic)

---

## Fallback Strategy

If Perplexity returns weak results:

```python
async def research_with_fallback(name, title, company):
    # Try Perplexity first
    results = await perplexity_research(name, title, company)
    
    # Check quality
    if len(results['findings']) < 2:
        # Fallback: Try different query
        results = await perplexity_research_alternative(name, company)
    
    # If still weak, return empty with message
    if len(results['findings']) == 0:
        return {
            "findings": [],
            "message": "No significant public content found. Try manual research."
        }
    
    return results
```

---

## Next Steps

Once you have the Perplexity API key:

1. Add to `.env` file
2. I'll implement the research module
3. Add API endpoint
4. Build UI (research button + results modal)
5. Test with real prospects
6. Deploy

**Estimated time**: 3-4 hours for full implementation

---

## Questions to Consider

1. **Model choice**: Start with `sonar-small` (cheapest) or `sonar-large` (better)?
2. **Cache duration**: How long to cache research results? (Recommend: 7 days)
3. **Rate limiting**: Any daily research limits? (Recommend: 100/day to start)
4. **UI placement**: Button next to name field or separate "Research" tab?
5. **Auto-research**: Trigger on LinkedIn URL paste or manual button only?

Let me know when you have the API key and your preferences! 🚀
