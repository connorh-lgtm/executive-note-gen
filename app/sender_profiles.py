"""
Sender profiles with personal facts for more natural connections
"""

SENDER_PROFILES = {
    "Jake": {
        "background": [
            "MN native (Minnesota)",
            "Lived in Hong Kong and Japan",
            "Frequent travel to Singapore",
            "Individual Tax Preparer for low-income households (volunteer work)"
        ],
        "interests": [
            "Asian food and culture",
            "Service and giving back to community",
            "Access to information and education"
        ]
    },
    "Graham": {
        "background": [
            "Worked at Grafana Labs",
            "Worked at MongoDB",
            "Grew up playing soccer in Austin"
        ],
        "interests": [
            "Food and travel",
            "Soccer",
            "Exploring new places and cuisines"
        ]
    },
    "Sandeep": {
        "background": [
            "Worked at Grafana Labs",
            "Went to Santa Clara University",
            "Started his own business",
            "Deep experience with enterprise AI deployments"
        ],
        "interests": [
            "Avid Chicago sports fan",
            "Entrepreneurship and startups",
            "Technical innovation",
            "Real-world AI impact"
        ]
    }
}


def get_sender_context(manager_name: str) -> str:
    """
    Get sender profile context for prompt personalization
    
    Args:
        manager_name: Name of the sender
    
    Returns:
        Formatted context string for the prompt
    """
    # Extract first name
    first_name = manager_name.split()[0] if manager_name else manager_name
    
    profile = SENDER_PROFILES.get(first_name, None)
    
    if not profile:
        return ""
    
    context = f"\n[SENDER PROFILE - {first_name}]\n"
    context += "Background:\n"
    for item in profile["background"]:
        context += f"- {item}\n"
    context += "\nInterests:\n"
    for item in profile["interests"]:
        context += f"- {item}\n"
    context += "\nUse these personal facts ONLY if they naturally connect to the prospect's unique fact or background. Don't force connections.\n"
    
    return context
