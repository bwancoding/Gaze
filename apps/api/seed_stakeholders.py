#!/usr/bin/env python3
"""
Seed Script: Create sample stakeholders for testing
Creates realistic stakeholder groups for verification testing
"""

import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.stakeholders import StakeholderType, Stakeholder

def seed_stakeholders():
    db = SessionLocal()
    
    try:
        # Get stakeholder types
        types = {t.name: t for t in db.query(StakeholderType).all()}
        
        if not types:
            print("⚠ No stakeholder types found. Run migrate_add_stakeholders.py first!")
            return
        
        print("Creating sample stakeholders...\n")
        
        # Sample stakeholders by category
        stakeholders_data = [
            # Geopolitics - Countries
            ("Iranian Civilians", "Country", "Civilians living in Iran", "geopolitics"),
            ("Israeli Civilians", "Country", "Civilians living in Israel", "geopolitics"),
            ("US Citizens", "Country", "Citizens of the United States", "geopolitics"),
            ("Chinese Citizens", "Country", "Citizens of China", "geopolitics"),
            ("Russian Civilians", "Country", "Civilians living in Russia", "geopolitics"),
            ("Ukrainian Civilians", "Country", "Civilians living in Ukraine", "geopolitics"),
            
            # Geopolitics - Military
            ("IDF Personnel", "Military", "Israel Defense Forces members", "geopolitics"),
            ("Iranian Military", "Military", "Iranian armed forces members", "geopolitics"),
            ("US Military", "Military", "US armed forces members", "geopolitics"),
            
            # Geopolitics - Organizations
            ("United Nations", "Organization", "UN staff and affiliates", "geopolitics"),
            ("Red Cross", "Organization", "International Red Cross workers", "geopolitics"),
            ("Amnesty International", "Organization", "Human rights researchers", "geopolitics"),
            
            # Geopolitics - Groups
            ("Gaza Residents", "Group", "Civilians in Gaza Strip", "geopolitics"),
            ("West Bank Residents", "Group", "Civilians in West Bank", "geopolitics"),
            ("Tel Aviv Residents", "Group", "Civilians in Tel Aviv area", "geopolitics"),
            ("Tehran Residents", "Group", "Civilians in Tehran area", "geopolitics"),
            
            # Technology - Companies
            ("Google Employees", "Company", "Google staff and contractors", "technology"),
            ("Meta Employees", "Company", "Meta/Facebook staff", "technology"),
            ("OpenAI Researchers", "Company", "OpenAI research team", "technology"),
            
            # Experts
            ("Middle East Scholars", "Expert", "Academic researchers on Middle East", "all"),
            ("International Law Experts", "Expert", "Legal scholars in international law", "all"),
            ("Conflict Analysts", "Expert", "Professional conflict analysts", "all"),
        ]
        
        created_count = 0
        for name, type_name, description, category in stakeholders_data:
            stakeholder_type = types.get(type_name)
            if not stakeholder_type:
                print(f"  ⚠ Type not found: {type_name}")
                continue
            
            # Check if exists
            existing = db.query(Stakeholder).filter(Stakeholder.name == name).first()
            if existing:
                print(f"  ⚠ Already exists: {name}")
                continue
            
            stakeholder = Stakeholder(
                id=uuid.uuid4(),
                name=name,
                type_id=stakeholder_type.id,
                description=description,
                category=category,
                verification_required=True,
                verification_method="self_declaration",
                is_active=True,
            )
            
            db.add(stakeholder)
            db.commit()  # Commit individually to avoid UUID issues
            created_count += 1
            print(f"  ✓ Created: {name}")
        
        print(f"\n✅ Successfully created {created_count} stakeholders!")
        print("\nTest credentials:")
        print("  User: test@example.com / test123")
        print("  Admin: admin / wrhitw_admin_2026")
        print("\nTest URLs:")
        print("  User Apply: http://localhost:3001/verify")
        print("  Admin Review: http://localhost:3001/admin/verifications")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_stakeholders()
