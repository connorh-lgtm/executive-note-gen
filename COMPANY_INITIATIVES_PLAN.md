# Company Initiatives Management Feature - Implementation Plan

## Overview
Add a company initiatives management system that allows users to store and manage 5-10 key companies with 3 key initiative facts per company. This data will be used to auto-populate and enhance the email generation process.

---

## 1. Feature Requirements

### 1.1 Core Functionality
- **Company Management**: CRUD operations for 5-10 target companies
- **Initiative Tracking**: Store 3 key initiative facts per company
- **Auto-Population**: Automatically suggest initiatives when generating emails for known companies
- **Persistence**: Store data in a lightweight database (SQLite)
- **UI Integration**: Seamless integration with existing email generation workflow

### 1.2 User Stories
1. As a user, I want to add my key target companies so I can track them
2. As a user, I want to store 3 key initiatives per company for quick reference
3. As a user, I want the system to auto-suggest initiatives when I select a company
4. As a user, I want to edit/update company information as initiatives change
5. As a user, I want to delete companies I'm no longer targeting

---

## 2. Technical Architecture

### 2.1 Database Schema

```sql
-- Companies Table
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    industry TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initiatives Table
CREATE TABLE initiatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    source_url TEXT,
    priority INTEGER DEFAULT 1,  -- 1=high, 2=medium, 3=low
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CHECK (priority IN (1, 2, 3))
);

-- Index for faster lookups
CREATE INDEX idx_initiatives_company_id ON initiatives(company_id);
CREATE INDEX idx_companies_name ON companies(name);
```

### 2.2 Backend Structure

```
app/
├── main.py                    # Existing FastAPI app (add new routes)
├── generator.py               # Existing generator
├── database.py                # NEW: Database connection & setup
├── models.py                  # NEW: Pydantic models for companies/initiatives
├── crud.py                    # NEW: CRUD operations
└── schemas.py                 # NEW: API request/response schemas
```

### 2.3 API Endpoints

#### Company Endpoints
- `GET /api/companies` - List all companies
- `GET /api/companies/{id}` - Get company details with initiatives
- `POST /api/companies` - Create new company
- `PUT /api/companies/{id}` - Update company
- `DELETE /api/companies/{id}` - Delete company

#### Initiative Endpoints
- `GET /api/companies/{company_id}/initiatives` - Get initiatives for a company
- `POST /api/companies/{company_id}/initiatives` - Add initiative
- `PUT /api/initiatives/{id}` - Update initiative
- `DELETE /api/initiatives/{id}` - Delete initiative

#### Search/Autocomplete
- `GET /api/companies/search?q={query}` - Search companies by name

---

## 3. Frontend UI Design

### 3.1 New Components

#### A. Company Management Page (New Tab/Section)
```
┌─────────────────────────────────────────────────────┐
│  📊 My Target Companies                              │
│  ┌─────────────────────────────────────────────┐   │
│  │ [+ Add New Company]                          │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🏢 Acme Financial Services                   │   │
│  │    Industry: Financial Services              │   │
│  │    ✏️ Edit  🗑️ Delete                         │   │
│  │                                               │   │
│  │    Key Initiatives:                           │   │
│  │    1. 🎯 Scaling AI from 5 to 50 use cases   │   │
│  │    2. 🎯 Cloud migration to AWS by Q4        │   │
│  │    3. 🎯 Real-time fraud detection system    │   │
│  │       [+ Add Initiative]                      │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ 🏢 TechCorp Industries                       │   │
│  │    Industry: Technology                      │   │
│  │    ...                                        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

#### B. Enhanced Email Generation Form
```
┌─────────────────────────────────────────────────────┐
│  Company Name: [Acme Financial Services ▼]          │
│                 ↓ (autocomplete dropdown)            │
│                 [Acme Financial Services]            │
│                 [Acme Corp]                          │
│                 [+ Add New Company]                  │
│                                                      │
│  Business Initiative: [Select from saved ▼]         │
│                       ↓ (if company selected)        │
│                       [Scaling AI from 5 to 50...]  │
│                       [Cloud migration to AWS...]    │
│                       [Real-time fraud detection...] │
│                       [Custom (type your own)]       │
└─────────────────────────────────────────────────────┘
```

### 3.2 Navigation Updates
Add new tab/section to main navigation:
- **Generate Email** (existing)
- **My Companies** (new)
- **History** (existing sidebar)

---

## 4. Implementation Phases

### Phase 1: Backend Foundation (Day 1-2)
**Goal**: Set up database and API endpoints

#### Tasks:
1. **Database Setup**
   - [ ] Create `app/database.py` with SQLite connection
   - [ ] Create `app/models.py` with SQLAlchemy models
   - [ ] Create migration script for initial schema
   - [ ] Add database initialization to `app/main.py`

2. **CRUD Operations**
   - [ ] Create `app/crud.py` with company CRUD functions
   - [ ] Create initiative CRUD functions
   - [ ] Add error handling and validation

3. **API Endpoints**
   - [ ] Implement company endpoints in `app/main.py`
   - [ ] Implement initiative endpoints
   - [ ] Add search/autocomplete endpoint
   - [ ] Write API tests

4. **Dependencies**
   - [ ] Update `requirements.txt`:
     ```
     sqlalchemy==2.0.23
     aiosqlite==0.19.0
     ```

**Deliverable**: Fully functional REST API for company/initiative management

---

### Phase 2: Frontend UI (Day 3-4)
**Goal**: Build company management interface

#### Tasks:
1. **Company Management Page**
   - [ ] Create company list view with cards
   - [ ] Add "Add Company" modal/form
   - [ ] Add "Edit Company" modal/form
   - [ ] Implement delete with confirmation
   - [ ] Add initiative sub-list per company

2. **Initiative Management**
   - [ ] Add initiative form (inline or modal)
   - [ ] Edit/delete initiative buttons
   - [ ] Priority indicators (high/medium/low)
   - [ ] Character count for descriptions

3. **Navigation**
   - [ ] Add "My Companies" tab to header
   - [ ] Update routing (if using client-side routing)
   - [ ] Add active state indicators

4. **Styling**
   - [ ] Match existing Tailwind theme
   - [ ] Add hover states and animations
   - [ ] Ensure mobile responsiveness

**Deliverable**: Fully functional company management UI

---

### Phase 3: Integration with Email Generator (Day 5)
**Goal**: Connect company data to email generation workflow

#### Tasks:
1. **Autocomplete Integration**
   - [ ] Add company name autocomplete to email form
   - [ ] Fetch companies on input change
   - [ ] Handle "Add New Company" from dropdown

2. **Initiative Auto-Population**
   - [ ] Load initiatives when company is selected
   - [ ] Populate initiative dropdown
   - [ ] Allow custom initiative input
   - [ ] Pre-fill form fields

3. **Smart Suggestions**
   - [ ] Show most recent initiatives first
   - [ ] Highlight high-priority initiatives
   - [ ] Add "Use this initiative" quick action

4. **Backend Updates**
   - [ ] Modify `/api/generate` to accept `company_id`
   - [ ] Log which initiatives are used
   - [ ] Track usage statistics (optional)

**Deliverable**: Seamless integration between company data and email generation

---

### Phase 4: Polish & Testing (Day 6)
**Goal**: Ensure quality and user experience

#### Tasks:
1. **Error Handling**
   - [ ] Add validation messages
   - [ ] Handle network errors gracefully
   - [ ] Add loading states

2. **User Experience**
   - [ ] Add success/error toasts
   - [ ] Add empty states ("No companies yet")
   - [ ] Add keyboard shortcuts (optional)
   - [ ] Add confirmation dialogs for destructive actions

3. **Testing**
   - [ ] Test all CRUD operations
   - [ ] Test autocomplete edge cases
   - [ ] Test with 0, 1, 5, and 10 companies
   - [ ] Test mobile responsiveness

4. **Documentation**
   - [ ] Update README with new features
   - [ ] Add API documentation
   - [ ] Create user guide (optional)

**Deliverable**: Production-ready feature

---

## 5. Code Examples

### 5.1 Database Models (`app/models.py`)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    industry = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    initiatives = relationship("Initiative", back_populates="company", cascade="all, delete-orphan")

class Initiative(Base):
    __tablename__ = "initiatives"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    source_url = Column(String)
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = relationship("Company", back_populates="initiatives")
```

### 5.2 Pydantic Schemas (`app/schemas.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class InitiativeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    source_url: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=3)

class InitiativeCreate(InitiativeBase):
    pass

class InitiativeUpdate(InitiativeBase):
    pass

class Initiative(InitiativeBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    initiatives: List[Initiative] = []
    
    class Config:
        from_attributes = True

class CompanyList(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    initiative_count: int
```

### 5.3 CRUD Operations (`app/crud.py`)

```python
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models import Company, Initiative
from app.schemas import CompanyCreate, CompanyUpdate, InitiativeCreate, InitiativeUpdate

# Company CRUD
def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
    return db.query(Company).offset(skip).limit(limit).all()

def get_company(db: Session, company_id: int) -> Optional[Company]:
    return db.query(Company).filter(Company.id == company_id).first()

def get_company_by_name(db: Session, name: str) -> Optional[Company]:
    return db.query(Company).filter(Company.name == name).first()

def search_companies(db: Session, query: str) -> List[Company]:
    return db.query(Company).filter(
        Company.name.ilike(f"%{query}%")
    ).limit(10).all()

def create_company(db: Session, company: CompanyCreate) -> Company:
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def update_company(db: Session, company_id: int, company: CompanyUpdate) -> Optional[Company]:
    db_company = get_company(db, company_id)
    if db_company:
        for key, value in company.model_dump(exclude_unset=True).items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company

def delete_company(db: Session, company_id: int) -> bool:
    db_company = get_company(db, company_id)
    if db_company:
        db.delete(db_company)
        db.commit()
        return True
    return False

# Initiative CRUD
def get_initiatives(db: Session, company_id: int) -> List[Initiative]:
    return db.query(Initiative).filter(
        Initiative.company_id == company_id
    ).order_by(Initiative.priority, Initiative.created_at.desc()).all()

def create_initiative(db: Session, company_id: int, initiative: InitiativeCreate) -> Initiative:
    db_initiative = Initiative(**initiative.model_dump(), company_id=company_id)
    db.add(db_initiative)
    db.commit()
    db.refresh(db_initiative)
    return db_initiative

def update_initiative(db: Session, initiative_id: int, initiative: InitiativeUpdate) -> Optional[Initiative]:
    db_initiative = db.query(Initiative).filter(Initiative.id == initiative_id).first()
    if db_initiative:
        for key, value in initiative.model_dump(exclude_unset=True).items():
            setattr(db_initiative, key, value)
        db.commit()
        db.refresh(db_initiative)
    return db_initiative

def delete_initiative(db: Session, initiative_id: int) -> bool:
    db_initiative = db.query(Initiative).filter(Initiative.id == initiative_id).first()
    if db_initiative:
        db.delete(db_initiative)
        db.commit()
        return True
    return False
```

### 5.4 API Endpoints (add to `app/main.py`)

```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas

# Company endpoints
@app.get("/api/companies", response_model=List[schemas.Company])
async def list_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all companies with their initiatives"""
    companies = crud.get_companies(db, skip=skip, limit=limit)
    return companies

@app.get("/api/companies/search")
async def search_companies(q: str, db: Session = Depends(get_db)):
    """Search companies by name"""
    companies = crud.search_companies(db, q)
    return [{"id": c.id, "name": c.name, "industry": c.industry} for c in companies]

@app.get("/api/companies/{company_id}", response_model=schemas.Company)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get company details with initiatives"""
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.post("/api/companies", response_model=schemas.Company, status_code=201)
async def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company"""
    # Check if company already exists
    existing = crud.get_company_by_name(db, company.name)
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")
    return crud.create_company(db, company)

@app.put("/api/companies/{company_id}", response_model=schemas.Company)
async def update_company(company_id: int, company: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    """Update company details"""
    updated = crud.update_company(db, company_id, company)
    if not updated:
        raise HTTPException(status_code=404, detail="Company not found")
    return updated

@app.delete("/api/companies/{company_id}", status_code=204)
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company and all its initiatives"""
    success = crud.delete_company(db, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")

# Initiative endpoints
@app.get("/api/companies/{company_id}/initiatives", response_model=List[schemas.Initiative])
async def list_initiatives(company_id: int, db: Session = Depends(get_db)):
    """Get all initiatives for a company"""
    # Verify company exists
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return crud.get_initiatives(db, company_id)

@app.post("/api/companies/{company_id}/initiatives", response_model=schemas.Initiative, status_code=201)
async def create_initiative(company_id: int, initiative: schemas.InitiativeCreate, db: Session = Depends(get_db)):
    """Add a new initiative to a company"""
    # Verify company exists
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if company already has 3 initiatives (optional limit)
    existing_count = len(crud.get_initiatives(db, company_id))
    if existing_count >= 3:
        raise HTTPException(status_code=400, detail="Company already has maximum of 3 initiatives")
    
    return crud.create_initiative(db, company_id, initiative)

@app.put("/api/initiatives/{initiative_id}", response_model=schemas.Initiative)
async def update_initiative(initiative_id: int, initiative: schemas.InitiativeUpdate, db: Session = Depends(get_db)):
    """Update an initiative"""
    updated = crud.update_initiative(db, initiative_id, initiative)
    if not updated:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return updated

@app.delete("/api/initiatives/{initiative_id}", status_code=204)
async def delete_initiative(initiative_id: int, db: Session = Depends(get_db)):
    """Delete an initiative"""
    success = crud.delete_initiative(db, initiative_id)
    if not success:
        raise HTTPException(status_code=404, detail="Initiative not found")
```

### 5.5 Database Setup (`app/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base
import os

# SQLite database file
DATABASE_URL = "sqlite:///./executive_note_gen.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5.6 Frontend JavaScript (Autocomplete Example)

```javascript
// Company autocomplete
let companyTimeout;
const companyInput = document.getElementById('companyInput');
const companyDropdown = document.getElementById('companyDropdown');

companyInput.addEventListener('input', (e) => {
    clearTimeout(companyTimeout);
    const query = e.target.value;
    
    if (query.length < 2) {
        companyDropdown.classList.add('hidden');
        return;
    }
    
    companyTimeout = setTimeout(async () => {
        const response = await fetch(`/api/companies/search?q=${encodeURIComponent(query)}`);
        const companies = await response.json();
        
        // Render dropdown
        companyDropdown.innerHTML = companies.map(c => `
            <div class="p-2 hover:bg-gray-100 cursor-pointer" onclick="selectCompany(${c.id}, '${c.name}')">
                <div class="font-medium">${c.name}</div>
                <div class="text-xs text-gray-500">${c.industry || 'No industry'}</div>
            </div>
        `).join('');
        
        companyDropdown.classList.remove('hidden');
    }, 300);
});

async function selectCompany(companyId, companyName) {
    companyInput.value = companyName;
    companyDropdown.classList.add('hidden');
    
    // Load initiatives for this company
    const response = await fetch(`/api/companies/${companyId}/initiatives`);
    const initiatives = await response.json();
    
    // Populate initiative dropdown
    const initiativeSelect = document.getElementById('initiativeSelect');
    initiativeSelect.innerHTML = `
        <option value="">Select from saved initiatives...</option>
        ${initiatives.map(i => `
            <option value="${i.description}">${i.title}</option>
        `).join('')}
        <option value="custom">Custom (type your own)</option>
    `;
}
```

---

## 6. Database Migration

### Initial Setup Script

```python
# scripts/init_db.py
from app.database import init_db, SessionLocal
from app.models import Company, Initiative

def seed_sample_data():
    """Add sample data for testing"""
    db = SessionLocal()
    
    # Sample companies
    companies = [
        {
            "name": "Acme Financial Services",
            "industry": "Financial Services",
            "initiatives": [
                {"title": "AI Scale Initiative", "description": "Scaling AI use cases from 5 to 50 by Q4", "priority": 1},
                {"title": "Cloud Migration", "description": "Complete AWS migration by end of year", "priority": 1},
                {"title": "Fraud Detection", "description": "Real-time fraud detection system deployment", "priority": 2}
            ]
        },
        {
            "name": "TechCorp Industries",
            "industry": "Technology",
            "initiatives": [
                {"title": "Platform Modernization", "description": "Migrate legacy systems to microservices", "priority": 1},
                {"title": "Developer Productivity", "description": "Reduce deployment time from days to hours", "priority": 2}
            ]
        }
    ]
    
    for company_data in companies:
        initiatives_data = company_data.pop("initiatives")
        company = Company(**company_data)
        db.add(company)
        db.flush()
        
        for init_data in initiatives_data:
            initiative = Initiative(**init_data, company_id=company.id)
            db.add(initiative)
    
    db.commit()
    db.close()
    print("✅ Database initialized with sample data")

if __name__ == "__main__":
    print("🔧 Initializing database...")
    init_db()
    seed_sample_data()
```

---

## 7. Testing Strategy

### 7.1 Backend Tests

```python
# tests/test_companies.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_company():
    response = client.post("/api/companies", json={
        "name": "Test Corp",
        "industry": "Technology"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Test Corp"

def test_list_companies():
    response = client.get("/api/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_initiative():
    # First create a company
    company_response = client.post("/api/companies", json={
        "name": "Test Corp 2",
        "industry": "Finance"
    })
    company_id = company_response.json()["id"]
    
    # Then create initiative
    response = client.post(f"/api/companies/{company_id}/initiatives", json={
        "title": "Test Initiative",
        "description": "Test description",
        "priority": 1
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Initiative"

def test_search_companies():
    response = client.get("/api/companies/search?q=Test")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

### 7.2 Frontend Tests (Manual Checklist)

- [ ] Can add a new company
- [ ] Can edit company details
- [ ] Can delete company (with confirmation)
- [ ] Can add up to 3 initiatives per company
- [ ] Autocomplete shows matching companies
- [ ] Selecting company loads initiatives
- [ ] Initiative dropdown populates correctly
- [ ] Form validation works
- [ ] Mobile responsive design works
- [ ] Empty states display correctly

---

## 8. Future Enhancements (Optional)

### Phase 2 Features
1. **Import/Export**: CSV import for bulk company data
2. **Tags/Categories**: Tag companies by segment, region, etc.
3. **Analytics**: Track which initiatives generate best responses
4. **Collaboration**: Share company data across team
5. **Chrome Extension Integration**: Auto-capture initiatives from LinkedIn
6. **AI Suggestions**: Auto-suggest initiatives based on company news
7. **Initiative History**: Track changes to initiatives over time
8. **Reminders**: Alert when initiative data is stale (>90 days)

---

## 9. Success Metrics

### Quantitative
- [ ] Can manage 10 companies with 3 initiatives each
- [ ] Autocomplete responds in <300ms
- [ ] API endpoints respond in <100ms
- [ ] Zero data loss during CRUD operations
- [ ] Mobile UI works on screens 375px+

### Qualitative
- [ ] Users find it easy to add companies
- [ ] Initiative auto-population saves time
- [ ] UI feels integrated with existing design
- [ ] Feature reduces manual data entry

---

## 10. Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|----------------|
| Phase 1: Backend | 2 days | Working API with database |
| Phase 2: Frontend | 2 days | Company management UI |
| Phase 3: Integration | 1 day | Connected to email generator |
| Phase 4: Polish | 1 day | Production-ready feature |
| **Total** | **6 days** | **Complete feature** |

---

## 11. Dependencies Update

Add to `requirements.txt`:
```
sqlalchemy==2.0.23
aiosqlite==0.19.0
alembic==1.12.1  # Optional: for database migrations
```

---

## 12. Getting Started

### Step 1: Review Plan
- Read through this document
- Clarify any questions
- Adjust timeline if needed

### Step 2: Set Up Development
```bash
cd /Users/connorhaley/CascadeProjects/executive-note-gen
source venv/bin/activate
pip install sqlalchemy aiosqlite
```

### Step 3: Start with Phase 1
- Create database models
- Set up CRUD operations
- Build API endpoints
- Test with Postman/curl

### Step 4: Move to Frontend
- Build company management UI
- Add autocomplete
- Integrate with email form

---

## Questions to Consider

1. **Company Limit**: Should we enforce a hard limit of 10 companies?
2. **Initiative Limit**: Should we allow more than 3 initiatives per company?
3. **Data Backup**: Should we add export functionality for backup?
4. **Sharing**: Will multiple users need access to the same company data?
5. **Validation**: What validation rules for company names (duplicates, special chars)?

---

## Next Steps

1. ✅ Review this plan
2. ⏳ Approve or request changes
3. ⏳ Begin Phase 1 implementation
4. ⏳ Iterate based on feedback

---

**Document Version**: 1.0  
**Created**: 2025-10-15  
**Author**: Cascade AI  
**Status**: Draft - Awaiting Approval
