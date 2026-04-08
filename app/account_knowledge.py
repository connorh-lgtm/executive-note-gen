"""
Account knowledge system — reads company context from markdown files in accounts/
"""
import os
import re
import glob
import time


ACCOUNTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'accounts')

# Module-level cache (None = never loaded, {} = loaded but empty)
_cached_accounts: dict | None = None
_cached_file_count: int = 0
_cache_load_time: float = 0.0


def _parse_account_markdown(file_path: str) -> dict:
    """
    Parse an account markdown file into the dict structure expected by the rest of the app.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract company name from H1
    h1_match = re.search(r'^# (.+)', content, re.MULTILINE)
    company_name = h1_match.group(1).strip() if h1_match else os.path.splitext(os.path.basename(file_path))[0]

    # Split into ## sections
    sections: dict[str, str] = {}
    parts = re.split(r'^## ', content, flags=re.MULTILINE)
    for part in parts[1:]:  # skip preamble before first ##
        lines = part.split('\n', 1)
        header = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ''
        sections[header.lower()] = body

    # --- Overview ---
    industry = ''
    status = ''
    if 'overview' in sections:
        overview = sections['overview']
        m = re.search(r'\*\*Industry:\*\*\s*(.+)', overview)
        if m:
            industry = m.group(1).strip()
        m = re.search(r'\*\*Status:\*\*\s*(.+)', overview)
        if m:
            status = m.group(1).strip()

    # --- Situation ---
    situation: dict = {"focus": "", "challenges": [], "recent_activity": ""}
    if 'situation' in sections:
        sit_text = sections['situation']
        m = re.search(r'\*\*Focus:\*\*\s*(.+)', sit_text)
        if m:
            situation['focus'] = m.group(1).strip()
        m = re.search(r'\*\*Recent Activity:\*\*\s*(.+)', sit_text)
        if m:
            situation['recent_activity'] = m.group(1).strip()
        # Challenges are bullet points under ### Challenges
        challenges_match = re.search(r'### Challenges\s*\n((?:- .+\n?)+)', sit_text)
        if challenges_match:
            situation['challenges'] = [
                line.removeprefix('- ').strip()
                for line in challenges_match.group(1).strip().split('\n')
                if line.strip().startswith('-')
            ]

    # --- Key Initiatives ---
    key_initiatives: list[str] = []
    if 'key initiatives' in sections:
        for line in sections['key initiatives'].strip().split('\n'):
            line = line.strip()
            if line.startswith('-'):
                key_initiatives.append(line.removeprefix('- ').strip())

    # --- Positioning ---
    positioning: dict = {"focus": "", "differentiators": [], "competitive": ""}
    if 'positioning' in sections:
        pos_text = sections['positioning']
        m = re.search(r'\*\*Focus:\*\*\s*(.+)', pos_text)
        if m:
            positioning['focus'] = m.group(1).strip()
        m = re.search(r'\*\*Competitive:\*\*\s*(.+)', pos_text)
        if m:
            positioning['competitive'] = m.group(1).strip()
        diff_match = re.search(r'### Differentiators\s*\n((?:- .+\n?)+)', pos_text)
        if diff_match:
            positioning['differentiators'] = [
                line.removeprefix('- ').strip()
                for line in diff_match.group(1).strip().split('\n')
                if line.strip().startswith('-')
            ]

    # --- Team Contacts ---
    team_contacts: dict[str, list[str]] = {}
    if 'team contacts' in sections:
        for m in re.finditer(r'\*\*(.+?):\*\*\s*(.+)', sections['team contacts']):
            team_key = m.group(1).strip().lower().replace(' ', '_')
            contacts = [c.strip() for c in m.group(2).split(',')]
            team_contacts[team_key] = contacts

    # --- Contact Notes ---
    contact_notes: dict[str, dict] = {}
    if 'contact notes' in sections:
        cn_text = sections['contact notes']
        # Split by ### sub-headers
        contact_parts = re.split(r'^### ', cn_text, flags=re.MULTILINE)
        for cp in contact_parts[1:]:  # skip preamble
            cp_lines = cp.split('\n', 1)
            contact_name = cp_lines[0].strip()
            contact_body = cp_lines[1] if len(cp_lines) > 1 else ''
            entry: dict[str, str] = {}
            for field_match in re.finditer(r'\*\*(.+?):\*\*\s*(.+)', contact_body):
                field_key = field_match.group(1).strip().lower().replace(' ', '_')
                entry[field_key] = field_match.group(2).strip()
            if entry:
                contact_notes[contact_name] = entry

    return {
        "company_name": company_name,
        "industry": industry,
        "status": status,
        "situation": situation,
        "team_contacts": team_contacts,
        "key_initiatives": key_initiatives,
        "positioning": positioning,
        "contact_notes": contact_notes
    }


def _load_all_accounts() -> tuple[dict, int]:
    """
    Scan accounts/ for *.md files (excluding TEMPLATE.md), parse each, and return
    a tuple of (accounts dict keyed by uppercase company name, count of non-template files found).
    """
    accounts: dict = {}
    accounts_dir = os.path.normpath(ACCOUNTS_DIR)
    if not os.path.isdir(accounts_dir):
        return accounts, 0

    file_count = 0
    for md_path in glob.glob(os.path.join(accounts_dir, '*.md')):
        basename = os.path.basename(md_path)
        if basename.upper() == 'TEMPLATE.MD':
            continue
        file_count += 1
        try:
            account = _parse_account_markdown(md_path)
            key = account['company_name'].upper()
            accounts[key] = account
        except Exception:
            # Skip files that fail to parse
            continue

    return accounts, file_count


def _get_accounts() -> dict:
    """
    Return cached accounts, reloading if any .md file has been modified since last load.
    """
    global _cached_accounts, _cached_file_count, _cache_load_time

    accounts_dir = os.path.normpath(ACCOUNTS_DIR)
    if not os.path.isdir(accounts_dir):
        return {}

    # Check if cache needs to be initialized or refreshed
    needs_reload = _cached_accounts is None
    if not needs_reload:
        md_paths = set(glob.glob(os.path.join(accounts_dir, '*.md')))
        disk_file_count = len([p for p in md_paths if os.path.basename(p).upper() != 'TEMPLATE.MD'])
        if disk_file_count != _cached_file_count:
            needs_reload = True
        else:
            for md_path in md_paths:
                if os.path.getmtime(md_path) > _cache_load_time:
                    needs_reload = True
                    break

    if needs_reload:
        _cache_load_time = time.time()
        _cached_accounts, _cached_file_count = _load_all_accounts()

    return _cached_accounts


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
    accounts = _get_accounts()
    
    # Try exact match first
    if company_key in accounts:
        return accounts[company_key]
    
    # Try partial match
    for key in accounts:
        if company_key in key or key in company_key:
            return accounts[key]
    
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
    return list(_get_accounts().keys())
