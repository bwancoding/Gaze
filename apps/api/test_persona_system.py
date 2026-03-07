#!/usr/bin/env python3
"""
Test Persona System
测试身份认证系统
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models import User
from app.models.personas import UserPersona
import uuid

def test_persona_system():
    db = SessionLocal()
    
    try:
        # Get or create test user
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            print("⚠ Test user not found. Run create_test_user.py first")
            return
        
        print(f"✅ Test user: {user.email}")
        
        # Check existing personas
        existing = db.query(UserPersona).filter(UserPersona.user_id == user.id).all()
        print(f"📊 Existing personas: {len(existing)}")
        
        # Create test personas (up to 5)
        test_personas = [
            ("Iranian Civilian", "blue"),
            ("Tech Worker", "green"),
            ("Investor", "purple"),
            ("Climate Activist", "orange"),
            ("Healthcare Worker", "red"),
        ]
        
        for name, color in test_personas:
            # Check if exists
            exists = db.query(UserPersona).filter(
                UserPersona.user_id == user.id,
                UserPersona.persona_name == name
            ).first()
            
            if exists:
                print(f"  ⚠ Persona '{name}' already exists")
                continue
            
            # Create
            persona = UserPersona(
                id=uuid.uuid4(),
                user_id=user.id,
                persona_name=name,
                avatar_color=color,
                is_verified=False,
            )
            
            db.add(persona)
            db.commit()
            print(f"  ✅ Created persona: {name} ({color})")
        
        # Show all personas
        print("\n📋 All personas:")
        all_personas = db.query(UserPersona).filter(UserPersona.user_id == user.id).all()
        for p in all_personas:
            status = "✅ Verified" if p.is_verified else "⏳ Unverified"
            print(f"  - {p.persona_name} ({p.avatar_color}) - {status}")
        
        print("\n✅ Test completed!")
        print("\nNext steps:")
        print("1. Restart backend server")
        print("2. Test API: GET /api/personas")
        print("3. Test persona creation via API")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_persona_system()
