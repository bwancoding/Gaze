#!/usr/bin/env python3
"""
Create test user for stakeholder verification testing
"""

import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models import User
from app.utils.security import hash_password

def create_test_user():
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            print("⚠ Test user already exists")
            return
        
        # Create test user (password is hashed before storage)
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash=hash_password("test123"),  # 🔐 Hashed password
            display_name="Test User",
            is_active=True,
        )
        
        db.add(user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("\nLogin credentials:")
        print("  Email: test@example.com")
        print("  Password: test123")
        print("\nTest URL: http://localhost:3001/verify")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
