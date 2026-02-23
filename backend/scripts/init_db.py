"""
Database initialization script for TRL Monitoring System.
Creates necessary roles, organization units, and initial users.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Role, OrgUnit, UserRole, UserOrgUnit
from app.core.security import get_password_hash


def create_roles(db: Session):
    """Create all necessary roles"""
    roles_data = [
        {"name": "SuperAdmin", "hierarchy_level": 5, "permissions": {"*": "*"}},
        {"name": "Manager", "hierarchy_level": 4, "permissions": {"projects": ["create", "read", "update"], "approvals": ["approve"]}},
        {"name": "Assistant Manager", "hierarchy_level": 3, "permissions": {"projects": ["read", "update"], "approvals": ["review"]}},
        {"name": "Engineer", "hierarchy_level": 2, "permissions": {"projects": ["read"], "trl": ["create", "update"]}},
        {"name": "Scientist", "hierarchy_level": 2, "permissions": {"projects": ["read"], "trl": ["create", "update"]}},
    ]
    
    created_roles = {}
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if existing_role:
            print(f"Role '{role_data['name']}' already exists, skipping...")
            created_roles[role_data["name"]] = existing_role
        else:
            role = Role(
                name=role_data["name"],
                hierarchy_level=role_data["hierarchy_level"],
                permissions_json=role_data["permissions"]
            )
            db.add(role)
            db.flush()
            created_roles[role_data["name"]] = role
            print(f"✓ Created role: {role_data['name']} (Level {role_data['hierarchy_level']})")
    
    return created_roles


def create_org_units(db: Session):
    """Create sample organization units"""
    org_units_data = [
        {"code": "DRDO-HQ", "name": "DRDO Headquarters", "org_type": "Directorate", "parent_id": None},
        {"code": "DRDO-LAB-01", "name": "Defence Research Laboratory", "org_type": "Lab", "parent_id": None},
        {"code": "DRDO-DIV-01", "name": "Technology Development Division", "org_type": "Division", "parent_id": None},
    ]
    
    created_org_units = {}
    for org_data in org_units_data:
        existing_org = db.query(OrgUnit).filter(OrgUnit.code == org_data["code"]).first()
        if existing_org:
            print(f"Org Unit '{org_data['code']}' already exists, skipping...")
            created_org_units[org_data["code"]] = existing_org
        else:
            org = OrgUnit(
                code=org_data["code"],
                name=org_data["name"],
                org_type=org_data["org_type"],
                parent_id=org_data["parent_id"]
            )
            db.add(org)
            db.flush()
            created_org_units[org_data["code"]] = org
            print(f"✓ Created org unit: {org_data['name']} ({org_data['code']})")
    
    return created_org_units


def create_users(db: Session, roles: dict, org_units: dict):
    """Create initial users"""
    users_data = [
        {
            "username": "admin",
            "email": "admin@drdo.gov.in",
            "password": "admin123",  # Change this in production!
            "full_name": "System Administrator",
            "role": "SuperAdmin",
            "org_units": ["DRDO-HQ"]
        },
        {
            "username": "manager1",
            "email": "manager1@drdo.gov.in",
            "password": "manager123",
            "full_name": "Project Manager",
            "role": "Manager",
            "org_units": ["DRDO-LAB-01"]
        },
        {
            "username": "asst_manager1",
            "email": "asst.manager1@drdo.gov.in",
            "password": "asst123",
            "full_name": "Assistant Manager",
            "role": "Assistant Manager",
            "org_units": ["DRDO-LAB-01"]
        },
        {
            "username": "engineer1",
            "email": "engineer1@drdo.gov.in",
            "password": "engineer123",
            "full_name": "Test Engineer",
            "role": "Engineer",
            "org_units": ["DRDO-LAB-01"]
        },
        {
            "username": "scientist1",
            "email": "scientist1@drdo.gov.in",
            "password": "scientist123",
            "full_name": "Research Scientist",
            "role": "Scientist",
            "org_units": ["DRDO-LAB-01"]
        },
    ]
    
    created_users = {}
    for user_data in users_data:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            print(f"User '{user_data['username']}' already exists, skipping...")
            created_users[user_data["username"]] = existing_user
        else:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True
            )
            db.add(user)
            db.flush()
            
            # Assign role
            role = roles.get(user_data["role"])
            if role:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    org_unit_id=None  # Global role
                )
                db.add(user_role)
            
            # Assign org units
            for org_code in user_data["org_units"]:
                org_unit = org_units.get(org_code)
                if org_unit:
                    user_org = UserOrgUnit(
                        user_id=user.id,
                        org_unit_id=org_unit.id
                    )
                    db.add(user_org)
            
            created_users[user_data["username"]] = user
            print(f"✓ Created user: {user_data['username']} ({user_data['full_name']}) - Role: {user_data['role']}")
    
    return created_users


def main():
    """Main initialization function"""
    print("=" * 60)
    print("TRL Monitoring System - Database Initialization")
    print("=" * 60)
    print()
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created/verified")
    print()
    
    db: Session = SessionLocal()
    try:
        # Create roles
        print("Creating roles...")
        roles = create_roles(db)
        db.commit()
        print()
        
        # Create org units
        print("Creating organization units...")
        org_units = create_org_units(db)
        db.commit()
        print()
        
        # Create users
        print("Creating users...")
        users = create_users(db, roles, org_units)
        db.commit()
        print()
        
        print("=" * 60)
        print("Initialization completed successfully!")
        print("=" * 60)
        print()
        print("Default users created:")
        print("-" * 60)
        for username, user_data in [
            ("admin", "admin123"),
            ("manager1", "manager123"),
            ("asst_manager1", "asst123"),
            ("engineer1", "engineer123"),
            ("scientist1", "scientist123"),
        ]:
            print(f"  Username: {username:20} Password: {user_data}")
        print()
        print("⚠️  WARNING: Change default passwords in production!")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
