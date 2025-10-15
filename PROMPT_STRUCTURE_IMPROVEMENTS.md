# Mega Prompt Structure Enforcement - Improvements

## Problem
The LLM was not consistently following the mega prompt's specified structure, resulting in emails that:
- Skipped or reordered sections
- Omitted the mandatory Citi/Goldman social proof text
- Didn't follow the Hook → Business Case → Devin Value → Social Proof → CTA flow
- Had inconsistent formatting

## Solution
Enhanced both the **system prompt** and **user prompt** to enforce strict structure adherence.

---

## Changes Made

### 1. System Prompt Structure Enhancement

**Before:**
```
[CORE STRUCTURE]
Greeting: "Hi {{First Name}},"
Hook (1-2 sentences): ...
Business Case (2-3 sentences): ...
```

**After:**
```
[CORE STRUCTURE - FOLLOW THIS ORDER EXACTLY]
You MUST follow this structure in order. Do not skip sections or reorder them.

1. Greeting: "Hi {{First Name}},"
2. Hook (1-2 sentences): ...
3. Business Case (2-3 sentences): ...
4. Devin Value (2-3 sentences): ...
5. Social Proof (1-2 sentences): MANDATORY text...
6. Closing & CTA (1 sentence): ...
7. Signature: "Best," or "Cheers," + sender's first name
8. Optional Personal Note (ONLY if natural): ...

CRITICAL: The structure order is non-negotiable.
```

**Key Improvements:**
- ✅ Numbered steps (1-8) for clarity
- ✅ Explicit "MUST follow" language
- ✅ "Non-negotiable" emphasis
- ✅ Clear ordering statement at end

### 2. Social Proof Text Enforcement

**Before:**
```
Social Proof (1-2 sentences):
- ALWAYS include: "Devin, the AI software engineer..."
- OR rotate case studies: Nubank, Bilt, Gumroad...
```

**After:**
```
5. Social Proof (1-2 sentences):
   - MANDATORY: Include the FULL text: "Devin, the AI software engineer, has rolled out in production at [Citi](url) (American Banker: Citi Is Rolling Out Agentic AI To Its 40,000 Developers), [Goldman Sachs](url) (CNBC: Goldman Sachs is piloting its first autonomous coder in major AI milestone for Wall Street), and several of the largest financial services firms internationally. On average, banks see 6–12x efficiency gains on human engineering time with Devin."
   - MUST use exact markdown link format: [text](url) for Citi and Goldman Sachs
   - This text is non-negotiable and must appear verbatim
```

**Key Improvements:**
- ✅ Changed "ALWAYS" to "MANDATORY"
- ✅ Removed "OR rotate case studies" option (eliminated ambiguity)
- ✅ Added "non-negotiable and must appear verbatim"
- ✅ Specified exact markdown link format requirement

### 3. User Prompt Structure Checklist

**Before:**
```
Ensure the email:
- Uses the prospect's first name in greeting
- Incorporates the unique fact and business initiative naturally
- Includes Citi/Goldman validation OR uses the most relevant case study
- Follows the 80-110 word constraint strictly
```

**After:**
```
**CRITICAL: Follow the CORE STRUCTURE exactly as specified:**

1. **Greeting:** "Hi {{First Name}},"
2. **Hook (1-2 sentences):** Reference the unique fact, event, recognition, or initiative
3. **Business Case (2-3 sentences):** Frame the board-level tension/opportunity
4. **Devin Value (2-3 sentences):** 
   - Automates high-volume engineering work
   - 6-12x efficiency gains
   - Frees developers for innovation
5. **Social Proof (1-2 sentences):** 
   - MUST include: [Full Citi/Goldman text with markdown links]
6. **Closing & CTA (1 sentence):** Message-type-appropriate call to action
7. **Signature:** "Best," or "Cheers," followed by sender's first name
8. **Optional Personal Note:** Only if natural (1 sentence max)

**Strict Requirements:**
- Follow the structure order exactly: Hook → Business Case → Devin Value → Social Proof → CTA
- Include the FULL Citi/Goldman social proof text with markdown links
- NO deviations from the structure
```

**Key Improvements:**
- ✅ Numbered checklist format
- ✅ Explicit structure breakdown in user prompt
- ✅ "CRITICAL" and "Strict Requirements" sections
- ✅ Removed ambiguous "OR" options
- ✅ Clear flow diagram: Hook → Business Case → Devin Value → Social Proof → CTA

---

## Expected Output Structure

Every generated email should now follow this exact structure:

```
Hi [First Name],

[Hook: 1-2 sentences referencing unique fact/initiative]

[Business Case: 2-3 sentences framing the opportunity/challenge]

[Devin Value: 2-3 sentences on automation, 6-12x gains, freeing developers]

Devin, the AI software engineer, has rolled out in production at [Citi](https://www.americanbanker.com/news/citi-is-rolling-out-agentic-ai-to-its-40-000-developers) (American Banker: Citi Is Rolling Out Agentic AI To Its 40,000 Developers), [Goldman Sachs](https://www.cnbc.com/2025/07/11/goldman-sachs-autonomous-coder-pilot-marks-major-ai-milestone.html) (CNBC: Goldman Sachs is piloting its first autonomous coder in major AI milestone for Wall Street), and several of the largest financial services firms internationally. On average, banks see 6–12x efficiency gains on human engineering time with Devin.

[CTA: 1 sentence with specific ask]

Best,
[Sender First Name]

[Optional: Personal note if natural]
```

---

## Why This Matters

### 1. **Consistency**
Every email follows the proven structure that works for executive outreach.

### 2. **Social Proof**
The Citi/Goldman validation is the strongest credibility signal. It must appear in every email with proper markdown links for clickability.

### 3. **Readability**
The structure creates a natural flow:
- **Hook** → Grabs attention
- **Business Case** → Establishes relevance
- **Devin Value** → Shows solution
- **Social Proof** → Builds credibility
- **CTA** → Drives action

### 4. **Brand Consistency**
All outreach maintains the same high-quality, board-level tone.

---

## Testing the Changes

### Before Testing
Generate a few emails and check:
- ❌ Social proof text varied or was abbreviated
- ❌ Sections sometimes appeared in wrong order
- ❌ Markdown links sometimes missing
- ❌ Structure occasionally skipped sections

### After Testing
Generate emails and verify:
- ✅ Full Citi/Goldman text appears verbatim
- ✅ Markdown links formatted correctly: `[Citi](url)`
- ✅ Structure follows exact order: Hook → Business Case → Devin Value → Social Proof → CTA
- ✅ All sections present
- ✅ 80-110 word count maintained

### Test Command
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "Sarah Johnson",
    "prospect_title": "CTO",
    "prospect_company": "Acme Financial",
    "unique_fact": "Led digital transformation initiative",
    "business_initiative": "Scaling AI adoption across engineering teams",
    "manager_name": "Jake",
    "message_type": "cold_outreach"
  }'
```

---

## Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Structure Clarity** | Implicit | Explicit numbered steps |
| **Social Proof** | "ALWAYS include" | "MANDATORY, non-negotiable, verbatim" |
| **Order Enforcement** | Suggested | "MUST follow, non-negotiable" |
| **Markdown Links** | Mentioned | "MUST use exact format" |
| **Ambiguity** | "OR rotate case studies" | Removed - only Citi/Goldman |
| **User Prompt** | General checklist | Explicit structure breakdown |
| **Consistency** | Variable | Enforced |

---

## Key Language Changes

### Strengthened Directives

| Before | After | Impact |
|--------|-------|--------|
| "ALWAYS include" | "MANDATORY" | Stronger requirement |
| "Follow the structure" | "MUST follow this structure in order" | Explicit command |
| "Include Citi/Goldman" | "This text is non-negotiable and must appear verbatim" | No room for interpretation |
| "OR rotate case studies" | [Removed] | Eliminated ambiguity |
| "Ensure the email..." | "CRITICAL: Follow the CORE STRUCTURE exactly" | Elevated importance |

---

## Expected Benefits

### 1. **Higher Quality Emails**
- Consistent structure across all generations
- Proper social proof in every email
- Professional markdown formatting

### 2. **Better Conversion**
- Proven structure that works
- Strong credibility signals (Citi/Goldman)
- Clear, actionable CTAs

### 3. **Reduced Editing**
- Less manual cleanup needed
- Fewer missing sections
- Consistent formatting

### 4. **Brand Trust**
- Every email represents the same high standard
- Recipients see consistent, professional communication
- Builds recognition and trust over time

---

## Monitoring

After deployment, monitor:

1. **Structure Adherence Rate**
   - Check 10 random generations
   - Verify all 8 sections present in order
   - Target: 100% adherence

2. **Social Proof Inclusion**
   - Verify full Citi/Goldman text present
   - Check markdown links formatted correctly
   - Target: 100% inclusion

3. **Word Count Compliance**
   - Verify 80-110 words (excluding greeting/signature)
   - Target: 95%+ compliance

4. **User Feedback**
   - Ask users if emails feel more consistent
   - Check if manual editing decreased
   - Monitor email response rates

---

## Future Enhancements (Optional)

### 1. Post-Generation Validation
Add a validation function to check structure:
```python
def validate_email_structure(body: str) -> dict:
    """Validate email follows required structure"""
    checks = {
        "has_greeting": bool(re.search(r"^Hi \w+,", body)),
        "has_citi_goldman": "Citi" in body and "Goldman Sachs" in body,
        "has_markdown_links": "[Citi](" in body and "[Goldman Sachs](" in body,
        "word_count": 80 <= len(body.split()) <= 110
    }
    return checks
```

### 2. Structure Scoring
Rate each generation on structure adherence:
```python
def score_structure(body: str) -> float:
    """Score 0-100 based on structure adherence"""
    score = 0
    if has_greeting(body): score += 15
    if has_hook(body): score += 15
    if has_business_case(body): score += 15
    if has_devin_value(body): score += 15
    if has_full_social_proof(body): score += 25
    if has_cta(body): score += 15
    return score
```

### 3. Automatic Retry
If structure validation fails, retry generation:
```python
async def generate_with_validation(request):
    max_retries = 3
    for attempt in range(max_retries):
        result = await generate_outreach_emails(...)
        if validate_email_structure(result["body"]):
            return result
        print(f"Structure validation failed, retry {attempt + 1}")
    return result  # Return last attempt
```

---

## Summary

These changes transform the prompt from **suggestive** to **prescriptive**:

| Aspect | Before | After |
|--------|--------|-------|
| **Tone** | Suggestive | Prescriptive |
| **Clarity** | Implicit | Explicit |
| **Enforcement** | Weak | Strong |
| **Ambiguity** | Some options | No options |
| **Structure** | Described | Mandated |

**Result**: LLM now has clear, unambiguous instructions that enforce the mega prompt structure exactly as designed.

---

**Implementation Date**: 2025-10-15  
**Status**: ✅ Complete and Deployed  
**Files Changed**: `app/prompts_v2.py`  
**Impact**: High - Ensures consistent, high-quality email generation
