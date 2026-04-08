"""
Model client for Anthropic API
"""
import os
import json
import re
from typing import Optional


async def call_anthropic(system_prompt: str, user_prompt: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Call Anthropic API"""
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
    provider: str = "anthropic",
    model: Optional[str] = None
) -> dict:
    """
    Generate content using Anthropic
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        provider: Ignored (kept for backward compatibility)
        model: Optional model override
    
    Returns:
        Parsed JSON response
    """
    return await call_anthropic(system_prompt, user_prompt, model or "claude-sonnet-4-20250514")
