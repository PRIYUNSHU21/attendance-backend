"""
🏢 ORGANIZATION MODEL - models/organisation.py

🎯 WHAT THIS FILE DOES:
This file defines the Organization data structure and manages organization data.
Think of it as the "company/school profile" that groups users and attendance sessions.

🔧 FOR FRONTEND DEVELOPERS:
- Organizations are like "tenants" - each school/company is separate
- Users belong to one organization and can only see data from their org
- All attendance sessions and reports are scoped to the user's organization
- Admin features often work at the organization level

📋 ORGANIZATION DATA STRUCTURE (API Response Format):
{
  "org_id": "unique-uuid-string",
  "name": "Tech University",
  "description": "Leading technology education institution",
  "address": "123 Campus Drive, Tech City, TC 12345",
  "contact_email": "admin@techuniversity.edu",
  "contact_phone": "+1-555-123-4567",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-07-05T10:30:00Z",
  "is_active": true
}

🌐 AVAILABLE FUNCTIONS FOR FRONTEND:
- create_organisation(): Add new organization (super admin only)
- find_organisation_by_id(): Get organization details
- update_organisation(): Edit organization info
- get_all_organisations(): List all organizations (super admin only)

⚡ FRONTEND INTEGRATION EXAMPLES:
- User Profile: Shows which organization user belongs to
- Admin Dashboard: Organization stats and settings
- Reports: Filtered by user's organization
- Session Management: Sessions are created within organization

🏢 MULTI-TENANT ARCHITECTURE:
- Each organization is completely isolated
- Users from Organization A cannot see Organization B's data
- Attendance sessions are scoped to organizations
- Reports and analytics are per-organization

🔒 SECURITY & ACCESS:
- Regular users only see their own organization
- Organization admins can manage their organization
- Super admins can see and manage all organizations
- Cross-organization data access is prevented

📱 EXAMPLE FRONTEND USAGE:
// Organization info in user context
{
  "user": {
    "name": "John Doe",
    "org_id": "org-123",
    "organization": {
      "name": "Tech University",
      "address": "123 Campus Drive"
    }
  }
}

🎯 USE CASES:
- School districts with multiple schools
- Companies with multiple departments
- Training organizations with different programs
- Any system needing data separation by organization
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from config.db import db

class Organisation(db.Model):
    """Model for organizations/institutions."""
    __tablename__ = 'organisations'
    
    org_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Organisation {self.name}>'
    
    def to_dict(self):
        return {
            'org_id': self.org_id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

def create_organisation(data):
    """Create a new organisation."""
    try:
        org = Organisation(
            name=data["name"],
            description=data.get("description"),
            address=data.get("address"),
            contact_email=data.get("contact_email"),
            contact_phone=data.get("contact_phone")
        )
        db.session.add(org)
        db.session.commit()
        return org
    except Exception as e:
        db.session.rollback()
        raise e

def find_organisation_by_id(org_id):
    """Find an organisation by its ID."""
    return Organisation.query.filter_by(org_id=org_id, is_active=True).first()

def get_all_organisations():
    """Get all active organisations."""
    return Organisation.query.filter_by(is_active=True).all()

def update_organisation(org_id, data):
    """Update an existing organisation."""
    try:
        org = find_organisation_by_id(org_id)
        if not org:
            return None
        
        for key, value in data.items():
            if hasattr(org, key) and key != 'org_id':
                setattr(org, key, value)
        
        org.updated_at = datetime.utcnow()
        db.session.commit()
        return org
    except Exception as e:
        db.session.rollback()
        raise e