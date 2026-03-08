#!/usr/bin/env python3
"""
Create admin user for testing
"""

import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models import User
from app.utils.security import hash_password

def create_admin():
    db = SessionLocal()
    
    try:
        # Check if admin exists
        existing = db.query(User).filter(User.email == "admin").first()
        if existing:
            print("⚠ Admin user already exists")
            return
        
        # Create admin user (password is hashed before storage)
        admin = User(
            id=uuid.uuid4(),
            email="admin",
            password_hash=hash_password("wrhitw_admin_2026"),  # 🔐 Hashed password
            display_name="Admin",
            is_active=True,
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("\nLogin credentials:")
        print("  Username: admin")
        print("  Password: wrhitw_admin_2026")
        print("\nAdmin URLs:")
        print("  Dashboard: http://localhost:3002/admin")
        print("  Verifications: http://localhost:3002/admin/verifications")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
