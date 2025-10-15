# Company Initiatives - Simplified Implementation Plan

## Overview
A lightweight company initiatives feature using JSON file storage instead of a database. Can be implemented in **2-3 days** instead of 6.

---

## Simplified Approach

### What We're Cutting
- ❌ SQLite database (use JSON file instead)
- ❌ Separate company management page (integrate into main form)
- ❌ Full CRUD UI (simple modal forms)
- ❌ Complex search (basic filtering)
- ❌ Priority levels (just store 3 initiatives)

### What We're Keeping
- ✅ Store 5-10 companies with 3 initiatives each
- ✅ Autocomplete company selection
- ✅ Auto-populate initiatives
- ✅ Add/edit/delete functionality
- ✅ Persistent storage

---

## Technical Design

### Data Storage: JSON File

```json
{
  "companies": [
    {
      "id": "uuid-1",
      "name": "Acme Financial Services",
      "industry": "Financial Services",
      "initiatives": [
        "Scaling AI use cases from 5 to 50 by Q4",
        "Complete AWS cloud migration by year-end",
        "Deploy real-time fraud detection system"
      ],
      "created_at": "2025-10-15T10:00:00Z",
      "updated_at": "2025-10-15T10:00:00Z"
    }
  ]
}
```

### File Structure
```
app/
├── main.py              # Add new endpoints
├── companies_data.py    # NEW: JSON file operations
└── ...

data/
└── companies.json       # NEW: Data storage file
```

---

## Implementation Plan

### Phase 1: Backend (Day 1 - 4 hours)

#### 1. Create Data Manager (`app/companies_data.py`)
```python
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
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def _save_data(data: Dict):
    """Save companies to JSON file"""
    with open(DATA_FILE, 'w') as f:
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
    """Search companies by name"""
    companies = get_all_companies()
    query_lower = query.lower()
    return [c for c in companies if query_lower in c["name"].lower()]

def create_company(name: str, industry: str = "", initiatives: List[str] = None) -> Dict:
    """Create new company"""
    data = _load_data()
    
    # Check if company exists
    if any(c["name"].lower() == name.lower() for c in data["companies"]):
        raise ValueError("Company already exists")
    
    # Validate initiatives (max 3)
    if initiatives and len(initiatives) > 3:
        raise ValueError("Maximum 3 initiatives allowed")
    
    company = {
        "id": str(uuid.uuid4()),
        "name": name,
        "industry": industry,
        "initiatives": initiatives or [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    data["companies"].append(company)
    _save_data(data)
    return company

def update_company(company_id: str, name: str = None, industry: str = None, 
                   initiatives: List[str] = None) -> Optional[Dict]:
    """Update company"""
    data = _load_data()
    company = next((c for c in data["companies"] if c["id"] == company_id), None)
    
    if not company:
        return None
    
    if name:
        company["name"] = name
    if industry is not None:
        company["industry"] = industry
    if initiatives is not None:
        if len(initiatives) > 3:
            raise ValueError("Maximum 3 initiatives allowed")
        company["initiatives"] = initiatives
    
    company["updated_at"] = datetime.utcnow().isoformat()
    _save_data(data)
    return company

def delete_company(company_id: str) -> bool:
    """Delete company"""
    data = _load_data()
    original_count = len(data["companies"])
    data["companies"] = [c for c in data["companies"] if c["id"] != company_id]
    
    if len(data["companies"]) < original_count:
        _save_data(data)
        return True
    return False
```

#### 2. Add API Endpoints to `app/main.py`
```python
from app.companies_data import (
    get_all_companies, get_company, search_companies,
    create_company, update_company, delete_company
)
from pydantic import BaseModel
from typing import List, Optional

class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = ""
    initiatives: Optional[List[str]] = []

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    initiatives: Optional[List[str]] = None

@app.get("/api/companies")
async def list_companies():
    """Get all companies"""
    return {"companies": get_all_companies()}

@app.get("/api/companies/search")
async def search_companies_endpoint(q: str):
    """Search companies by name"""
    results = search_companies(q)
    return {"companies": results}

@app.get("/api/companies/{company_id}")
async def get_company_endpoint(company_id: str):
    """Get company by ID"""
    company = get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.post("/api/companies", status_code=201)
async def create_company_endpoint(company: CompanyCreate):
    """Create new company"""
    try:
        new_company = create_company(
            name=company.name,
            industry=company.industry or "",
            initiatives=company.initiatives or []
        )
        return new_company
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/companies/{company_id}")
async def update_company_endpoint(company_id: str, company: CompanyUpdate):
    """Update company"""
    try:
        updated = update_company(
            company_id=company_id,
            name=company.name,
            industry=company.industry,
            initiatives=company.initiatives
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Company not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/companies/{company_id}", status_code=204)
async def delete_company_endpoint(company_id: str):
    """Delete company"""
    success = delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")
```

**Tasks:**
- [ ] Create `app/companies_data.py`
- [ ] Add endpoints to `app/main.py`
- [ ] Test with curl/Postman
- [ ] Create `data/` directory

---

### Phase 2: Frontend Integration (Day 2 - 4 hours)

#### 1. Add Company Management Modal to `static/index.html`

Add button in header:
```html
<button onclick="openCompanyModal()" class="bg-white text-purple-600 px-4 py-2 rounded-lg hover:bg-gray-100">
    📊 My Companies
</button>
```

Add modal at end of body:
```html
<!-- Company Management Modal -->
<div id="companyModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
    <div class="bg-white rounded-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">My Target Companies</h2>
            <button onclick="closeCompanyModal()" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <!-- Add Company Form -->
        <div class="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 class="font-semibold mb-3">Add New Company</h3>
            <div class="space-y-3">
                <input type="text" id="newCompanyName" placeholder="Company Name" 
                       class="w-full px-3 py-2 border rounded-lg">
                <input type="text" id="newCompanyIndustry" placeholder="Industry (optional)" 
                       class="w-full px-3 py-2 border rounded-lg">
                <input type="text" id="newInitiative1" placeholder="Initiative 1" 
                       class="w-full px-3 py-2 border rounded-lg">
                <input type="text" id="newInitiative2" placeholder="Initiative 2" 
                       class="w-full px-3 py-2 border rounded-lg">
                <input type="text" id="newInitiative3" placeholder="Initiative 3" 
                       class="w-full px-3 py-2 border rounded-lg">
                <button onclick="addCompany()" 
                        class="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700">
                    Add Company
                </button>
            </div>
        </div>
        
        <!-- Companies List -->
        <div id="companiesList" class="space-y-4">
            <!-- Populated by JavaScript -->
        </div>
    </div>
</div>
```

#### 2. Add JavaScript Functions

```javascript
// Company Modal Management
function openCompanyModal() {
    document.getElementById('companyModal').classList.remove('hidden');
    loadCompanies();
}

function closeCompanyModal() {
    document.getElementById('companyModal').classList.add('hidden');
}

async function loadCompanies() {
    try {
        const response = await fetch('/api/companies');
        const data = await response.json();
        const companies = data.companies;
        
        const listEl = document.getElementById('companiesList');
        
        if (companies.length === 0) {
            listEl.innerHTML = '<p class="text-gray-500 text-center py-8">No companies yet. Add one above!</p>';
            return;
        }
        
        listEl.innerHTML = companies.map(company => `
            <div class="border rounded-lg p-4 hover:shadow-md transition">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <h3 class="font-bold text-lg">${company.name}</h3>
                        <p class="text-sm text-gray-600">${company.industry || 'No industry'}</p>
                    </div>
                    <button onclick="deleteCompany('${company.id}')" 
                            class="text-red-500 hover:text-red-700">
                        🗑️
                    </button>
                </div>
                <div class="space-y-1">
                    <p class="text-sm font-semibold text-gray-700">Key Initiatives:</p>
                    ${company.initiatives.map((init, i) => `
                        <p class="text-sm text-gray-600">• ${init}</p>
                    `).join('')}
                    ${company.initiatives.length === 0 ? '<p class="text-sm text-gray-400">No initiatives</p>' : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading companies:', error);
        alert('Failed to load companies');
    }
}

async function addCompany() {
    const name = document.getElementById('newCompanyName').value.trim();
    const industry = document.getElementById('newCompanyIndustry').value.trim();
    const initiative1 = document.getElementById('newInitiative1').value.trim();
    const initiative2 = document.getElementById('newInitiative2').value.trim();
    const initiative3 = document.getElementById('newInitiative3').value.trim();
    
    if (!name) {
        alert('Company name is required');
        return;
    }
    
    const initiatives = [initiative1, initiative2, initiative3].filter(i => i);
    
    try {
        const response = await fetch('/api/companies', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name, industry, initiatives })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        // Clear form
        document.getElementById('newCompanyName').value = '';
        document.getElementById('newCompanyIndustry').value = '';
        document.getElementById('newInitiative1').value = '';
        document.getElementById('newInitiative2').value = '';
        document.getElementById('newInitiative3').value = '';
        
        // Reload list
        loadCompanies();
        
        alert('Company added successfully!');
    } catch (error) {
        console.error('Error adding company:', error);
        alert('Failed to add company: ' + error.message);
    }
}

async function deleteCompany(companyId) {
    if (!confirm('Are you sure you want to delete this company?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/companies/${companyId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete');
        }
        
        loadCompanies();
    } catch (error) {
        console.error('Error deleting company:', error);
        alert('Failed to delete company');
    }
}

// Autocomplete for main form
let companySearchTimeout;

async function setupCompanyAutocomplete() {
    const companyInput = document.getElementById('prospectCompany');
    const dropdown = document.createElement('div');
    dropdown.id = 'companyDropdown';
    dropdown.className = 'absolute z-10 w-full bg-white border rounded-lg shadow-lg mt-1 hidden max-h-60 overflow-y-auto';
    companyInput.parentElement.style.position = 'relative';
    companyInput.parentElement.appendChild(dropdown);
    
    companyInput.addEventListener('input', (e) => {
        clearTimeout(companySearchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            dropdown.classList.add('hidden');
            return;
        }
        
        companySearchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/api/companies/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                const companies = data.companies;
                
                if (companies.length === 0) {
                    dropdown.classList.add('hidden');
                    return;
                }
                
                dropdown.innerHTML = companies.map(c => `
                    <div class="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0" 
                         onclick="selectCompany('${c.id}', '${c.name.replace(/'/g, "\\'")}')">
                        <div class="font-medium">${c.name}</div>
                        <div class="text-xs text-gray-500">${c.industry || 'No industry'}</div>
                    </div>
                `).join('');
                
                dropdown.classList.remove('hidden');
            } catch (error) {
                console.error('Error searching companies:', error);
            }
        }, 300);
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!companyInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });
}

async function selectCompany(companyId, companyName) {
    // Set company name
    document.getElementById('prospectCompany').value = companyName;
    document.getElementById('companyDropdown').classList.add('hidden');
    
    // Load initiatives
    try {
        const response = await fetch(`/api/companies/${companyId}`);
        const company = await response.json();
        
        if (company.initiatives && company.initiatives.length > 0) {
            // Show initiative selector
            showInitiativeSelector(company.initiatives);
        }
    } catch (error) {
        console.error('Error loading company initiatives:', error);
    }
}

function showInitiativeSelector(initiatives) {
    const initiativeInput = document.getElementById('businessInitiative');
    
    // Create dropdown if it doesn't exist
    let selector = document.getElementById('initiativeSelector');
    if (!selector) {
        selector = document.createElement('div');
        selector.id = 'initiativeSelector';
        selector.className = 'bg-blue-50 border border-blue-200 rounded-lg p-3 mt-2';
        initiativeInput.parentElement.appendChild(selector);
    }
    
    selector.innerHTML = `
        <p class="text-sm font-semibold text-blue-800 mb-2">💡 Saved Initiatives:</p>
        <div class="space-y-1">
            ${initiatives.map((init, i) => `
                <button type="button" 
                        onclick="useInitiative('${init.replace(/'/g, "\\'")}')"
                        class="block w-full text-left text-sm bg-white hover:bg-blue-100 px-3 py-2 rounded border">
                    ${init}
                </button>
            `).join('')}
        </div>
    `;
}

function useInitiative(initiative) {
    document.getElementById('businessInitiative').value = initiative;
    document.getElementById('initiativeSelector')?.remove();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupCompanyAutocomplete();
});
```

**Tasks:**
- [ ] Add modal HTML to `index.html`
- [ ] Add JavaScript functions
- [ ] Add "My Companies" button to header
- [ ] Test add/delete/search functionality

---

### Phase 3: Polish (Day 3 - 2 hours)

#### Tasks:
- [ ] Add loading spinners
- [ ] Add success/error toasts
- [ ] Test edge cases (empty states, duplicates)
- [ ] Add form validation
- [ ] Test mobile responsiveness
- [ ] Update README

---

## Testing Checklist

### Backend
- [ ] Create company via API
- [ ] List all companies
- [ ] Search companies
- [ ] Update company
- [ ] Delete company
- [ ] Handle duplicate company names
- [ ] Enforce max 3 initiatives

### Frontend
- [ ] Open/close company modal
- [ ] Add new company with initiatives
- [ ] Delete company with confirmation
- [ ] Autocomplete shows matching companies
- [ ] Selecting company loads initiatives
- [ ] Initiative buttons populate form
- [ ] Empty states display correctly

---

## Quick Start Commands

```bash
# Day 1: Backend
cd /Users/connorhaley/CascadeProjects/executive-note-gen
source venv/bin/activate

# Create files
touch app/companies_data.py
mkdir -p data

# Test API
curl http://localhost:8000/api/companies

# Day 2: Frontend
# Edit static/index.html
# Test in browser at http://localhost:8000
```

---

## Sample Data for Testing

```bash
# Add via API
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Financial Services",
    "industry": "Financial Services",
    "initiatives": [
      "Scaling AI use cases from 5 to 50 by Q4",
      "Complete AWS cloud migration by year-end",
      "Deploy real-time fraud detection system"
    ]
  }'
```

---

## Timeline

| Day | Hours | Tasks |
|-----|-------|-------|
| Day 1 | 4h | Backend: JSON storage + API endpoints |
| Day 2 | 4h | Frontend: Modal + autocomplete + integration |
| Day 3 | 2h | Polish: Testing + error handling + docs |
| **Total** | **10h** | **Complete feature** |

---

## What's Different from Full Version?

| Feature | Full Version | Simple Version |
|---------|-------------|----------------|
| Storage | SQLite database | JSON file |
| UI | Separate page | Modal overlay |
| Search | Full-text search | Simple filtering |
| Validation | Complex rules | Basic checks |
| Testing | Unit tests | Manual testing |
| Migration | Alembic | Not needed |
| **Time** | **6 days** | **2-3 days** |

---

## Future Upgrades (If Needed)

If this simple version works well, we can later:
1. Migrate JSON → SQLite for better performance
2. Add separate company management page
3. Add edit functionality (currently delete + re-add)
4. Add export/import features
5. Add usage analytics

---

## Ready to Start?

This simplified version gets you 80% of the value in 33% of the time!

**Next Step**: Shall I start implementing Day 1 (Backend)?
