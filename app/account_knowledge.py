"""
Account knowledge system for storing and retrieving company-specific context
"""

# Account knowledge database
ACCOUNT_KNOWLEDGE = {
    "BMO": {
        "company_name": "BMO",
        "industry": "Banking",
        "status": "Active - Pilot in Jan/Feb",
        
        # Key context
        "situation": {
            "focus": "Becoming a leading digital bank, emphasis on US market",
            "challenges": [
                "Managing legacy systems (COBOL, mainframe, older Angular versions)",
                "Significant tech debt/toil and tribal knowledge",
                "Shared infrastructure teams and centralized governance slow adoption",
                "Already invested in GitHub and GitHub Copilot"
            ],
            "recent_activity": "Onsite presentation 10/28/25, currently vetting security"
        },
        
        # Key stakeholders we're working with
        "team_contacts": {
            "us_digital": ["Kaus", "Eric P"],
            "architecture": ["Seshu", "Raju", "Rajeev"],
            "ai_innovation": ["Raju", "Rajeev"],
            "canadian_business": ["Joe Larizza"]
        },
        
        # Use cases they care about
        "key_initiatives": [
            "COBOL/mainframe/legacy modernization",
            "Angular framework upgrades",
            "Security vulnerability remediation",
            "Bug triage and fixes",
            "Documentation and sequence diagrams for undocumented systems"
        ],
        
        # Messaging that resonates
        "positioning": {
            "focus": "Brownfield work, parallelizable tasks, governance & auditability",
            "differentiators": [
                "Agent vs IDE assistant (Copilot is synchronous, Devin is autonomous)",
                "Parallel sessions (100+ concurrent)",
                "Full command & action logs for governance",
                "Multi-repo and DeepWiki capabilities"
            ],
            "competitive": "Complement to GitHub Copilot, not replacement"
        },
        
        # Personal notes about contacts
        "contact_notes": {
            "Lakshmi": {
                "title": "SVP Engineering",
                "notes": "Missed Chicago onsite, involved with Hopeworks charity",
                "last_contact": "Follow-up after onsite"
            },
            "Sam": {
                "title": "Director",
                "notes": "Avid runner and hiker, rock climbing enthusiast",
                "met_at": "Chicago onsite"
            },
            "Mariusz": {
                "title": "Executive",
                "notes": "Led QuickPay launch, interested in InnoV8 Hackathon model"
            },
            "Tamekia": {
                "title": "Executive",
                "notes": "Key driver of Bank of the West merger (330+ systems), Celent Model Bank Award"
            },
            "Prasad": {
                "title": "Data Leader",
                "notes": "Quote: 'Organizations that succeed won't just govern data — they'll leverage it as a catalyst'"
            }
        }
    },
    
    # Template for adding more companies
    "TEMPLATE": {
        "company_name": "",
        "industry": "",
        "status": "",
        "situation": {
            "focus": "",
            "challenges": [],
            "recent_activity": ""
        },
        "team_contacts": {},
        "key_initiatives": [],
        "positioning": {
            "focus": "",
            "differentiators": [],
            "competitive": ""
        },
        "contact_notes": {}
    }
}


def get_account_context(company_name: str) -> dict:
    """
    Get account knowledge for a company
    
    Args:
        company_name: Company name (case-insensitive)
    
    Returns:
        Account context dict or None if not found
    """
    # Normalize company name
    company_key = company_name.upper().strip()
    
    # Try exact match first
    if company_key in ACCOUNT_KNOWLEDGE:
        return ACCOUNT_KNOWLEDGE[company_key]
    
    # Try partial match (skip TEMPLATE entry)
    for key in ACCOUNT_KNOWLEDGE.keys():
        if key == "TEMPLATE":
            continue
        if company_key in key or key in company_key:
            return ACCOUNT_KNOWLEDGE[key]
    
    return None


def get_contact_context(prospect_name: str, company_name: str) -> dict:
    """
    Get contact-specific notes
    
    Args:
        prospect_name: Contact's name
        company_name: Company name
    
    Returns:
        Contact context dict or None if not found
    """
    account = get_account_context(company_name)
    if not account:
        return None
    
    contact_notes = account.get("contact_notes", {})
    
    # Try exact match
    if prospect_name in contact_notes:
        return contact_notes[prospect_name]
    
    # Try first name match
    first_name = prospect_name.split()[0] if prospect_name else ""
    if first_name in contact_notes:
        return contact_notes[first_name]
    
    return None


def format_account_context_for_prompt(company_name: str, prospect_name: str = "") -> str:
    """
    Format account context for injection into prompt
    
    Args:
        company_name: Company name
        prospect_name: Optional prospect name for contact-specific context
    
    Returns:
        Formatted context string
    """
    account = get_account_context(company_name)
    if not account:
        return ""
    
    context_parts = []
    
    # Company situation
    if "situation" in account:
        sit = account["situation"]
        context_parts.append(f"COMPANY CONTEXT ({company_name}):")
        if "focus" in sit:
            context_parts.append(f"- Focus: {sit['focus']}")
        if "challenges" in sit and sit["challenges"]:
            context_parts.append(f"- Challenges: {', '.join(sit['challenges'][:2])}")
        if "recent_activity" in sit:
            context_parts.append(f"- Recent: {sit['recent_activity']}")
    
    # Team contacts
    if "team_contacts" in account:
        teams = account["team_contacts"]
        all_contacts = []
        for team, contacts in teams.items():
            all_contacts.extend(contacts)
        if all_contacts:
            context_parts.append(f"- Working with: {', '.join(all_contacts[:5])}")
    
    # Key initiatives
    if "key_initiatives" in account and account["key_initiatives"]:
        initiatives = account["key_initiatives"][:3]
        context_parts.append(f"- Key initiatives: {', '.join(initiatives)}")
    
    # Contact-specific notes
    if prospect_name:
        contact = get_contact_context(prospect_name, company_name)
        if contact:
            context_parts.append(f"\nCONTACT CONTEXT ({prospect_name}):")
            if "title" in contact:
                context_parts.append(f"- Title: {contact['title']}")
            if "notes" in contact:
                context_parts.append(f"- Notes: {contact['notes']}")
            if "last_contact" in contact:
                context_parts.append(f"- Last contact: {contact['last_contact']}")
    
    return "\n".join(context_parts)


def list_known_accounts() -> list:
    """Get list of companies with account knowledge"""
    return [k for k in ACCOUNT_KNOWLEDGE.keys() if k != "TEMPLATE"]
