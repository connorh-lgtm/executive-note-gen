"""
Model provider abstraction for OpenAI and Anthropic
"""
import os
import json
import re
from typing import Optional


async def call_openai(system_prompt: str, user_prompt: str, model: str = "gpt-4o") -> dict:
    """Call OpenAI API"""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = openai.AsyncOpenAI(api_key=api_key)
    
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    
    content = response.choices[0].message.content
    return parse_json_response(content)


async def call_anthropic(system_prompt: str, user_prompt: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Call Anthropic API and return JSON"""
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = anthropic.AsyncAnthropic(api_key=api_key)
    
    response = await client.messages.create(
        model=model,
        max_tokens=4000,
        temperature=0.7,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    content = response.content[0].text
    return parse_json_response(content)


async def call_anthropic_text(system_prompt: str, user_prompt: str, model: str = "claude-sonnet-4-20250514") -> str:
    """Call Anthropic API and return plain text (for non-JSON responses)"""
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = anthropic.AsyncAnthropic(api_key=api_key)
    
    response = await client.messages.create(
        model=model,
        max_tokens=4000,
        temperature=0.7,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.content[0].text


def parse_json_response(content: str) -> dict:
    """
    Parse JSON from model response, handling markdown code fences
    """
    # Remove markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        # Extract content between code fences
        match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
        if match:
            content = match.group(1)
        else:
            # Try removing just the fences
            content = re.sub(r'```(?:json)?', '', content).strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {e}\nContent: {content[:500]}")


async def generate_with_model(
    system_prompt: str,
    user_prompt: str,
    provider: str = "openai",
    model: Optional[str] = None
) -> dict:
    """
    Generate content using specified model provider
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        provider: "openai" or "anthropic"
        model: Optional model override
    
    Returns:
        Parsed JSON response
    """
    provider = provider.lower()
    
    if provider == "openai":
        return await call_openai(system_prompt, user_prompt, model or "gpt-4o")
    elif provider == "anthropic":
        return await call_anthropic(system_prompt, user_prompt, model or "claude-sonnet-4-20250514")
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'anthropic'")
