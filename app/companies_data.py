"""
Company and initiatives data management using JSON file storage
"""
import json
import os
from typing import List, Optional, Dict
from datetime import datetime
import uuid

DATA_FILE = "data/companies.json"


def _load_data() -> Dict:
    """Load companies from JSON file"""
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        return {"companies": []}
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"companies": []}


def _save_data(data: Dict):
    """Save companies to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def get_all_companies() -> List[Dict]:
    """Get all companies"""
    data = _load_data()
    return data.get("companies", [])


def get_company(company_id: str) -> Optional[Dict]:
    """Get company by ID"""
    companies = get_all_companies()
    return next((c for c in companies if c["id"] == company_id), None)


def search_companies(query: str) -> List[Dict]:
    """Search companies by name (case-insensitive)"""
    companies = get_all_companies()
    query_lower = query.lower()
    return [c for c in companies if query_lower in c["name"].lower()]


def create_company(name: str, industry: str = "", initiatives: List[str] = None) -> Dict:
    """
    Create new company
    
    Args:
        name: Company name (required)
        industry: Industry/sector (optional)
        initiatives: List of up to 3 initiatives (optional)
    
    Returns:
        Created company dict
    
    Raises:
        ValueError: If company exists or too many initiatives
    """
    data = _load_data()
    
    # Check if company exists
    if any(c["name"].lower() == name.lower() for c in data["companies"]):
        raise ValueError("Company already exists")
    
    # Validate initiatives (max 3)
    if initiatives and len(initiatives) > 3:
        raise ValueError("Maximum 3 initiatives allowed")
    
    # Filter out empty initiatives
    if initiatives:
        initiatives = [i.strip() for i in initiatives if i.strip()]
    
    company = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "industry": industry.strip() if industry else "",
        "initiatives": initiatives or [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    data["companies"].append(company)
    _save_data(data)
    return company


def update_company(
    company_id: str, 
    name: str = None, 
    industry: str = None, 
    initiatives: List[str] = None
) -> Optional[Dict]:
    """
    Update company
    
    Args:
        company_id: Company ID
        name: New name (optional)
        industry: New industry (optional)
        initiatives: New initiatives list (optional)
    
    Returns:
        Updated company dict or None if not found
    
    Raises:
        ValueError: If too many initiatives
    """
    data = _load_data()
    company = next((c for c in data["companies"] if c["id"] == company_id), None)
    
    if not company:
        return None
    
    if name is not None:
        company["name"] = name.strip()
    if industry is not None:
        company["industry"] = industry.strip()
    if initiatives is not None:
        # Filter out empty initiatives
        initiatives = [i.strip() for i in initiatives if i.strip()]
        if len(initiatives) > 3:
            raise ValueError("Maximum 3 initiatives allowed")
        company["initiatives"] = initiatives
    
    company["updated_at"] = datetime.utcnow().isoformat()
    _save_data(data)
    return company


def delete_company(company_id: str) -> bool:
    """
    Delete company
    
    Args:
        company_id: Company ID
    
    Returns:
        True if deleted, False if not found
    """
    data = _load_data()
    original_count = len(data["companies"])
    data["companies"] = [c for c in data["companies"] if c["id"] != company_id]
    
    if len(data["companies"]) < original_count:
        _save_data(data)
        return True
    return False


def get_company_count() -> int:
    """Get total number of companies"""
    return len(get_all_companies())
