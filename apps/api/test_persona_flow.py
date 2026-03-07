#!/usr/bin/env python3
"""
简化为单一 Persona 体系后的测试流程
所有认证都通过 Persona 进行（事件级验证）
"""

import requests
from requests.auth import HTTPBasicAuth

API_BASE = "http://localhost:8080/api"

# Test credentials
USER_EMAIL = "test@example.com"
USER_PASS = "test123"
ADMIN_USER = "admin"
ADMIN_PASS = "wrhitw_admin_2026"

def test_persona_system():
    print("🧪 Testing Persona-based Verification System\n")
    
    # Test 1: Get my personas (user)
    print("1. Testing GET /personas (user)...")
    try:
        resp = requests.get(
            f"{API_BASE}/personas",
            auth=HTTPBasicAuth(USER_EMAIL, USER_PASS)
        )
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! User has {len(data.get('items', []))} personas")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Create a persona
    print("\n2. Testing POST /personas (create)...")
    try:
        resp = requests.post(
            f"{API_BASE}/personas",
            auth=HTTPBasicAuth(USER_EMAIL, USER_PASS),
            json={
                "persona_name": "Test Civilian",
                "avatar_color": "blue"
            }
        )
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! Created persona: {data.get('id', 'unknown')}")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get stakeholders (public)
    print("\n3. Testing GET /stakeholders/list (public)...")
    try:
        resp = requests.get(f"{API_BASE}/stakeholders/list")
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! Found {len(data.get('items', []))} stakeholders")
            if data.get('items'):
                print(f"   Sample: {data['items'][0]['name']} ({data['items'][0]['category']})")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get events
    print("\n4. Testing GET /events (public)...")
    try:
        resp = requests.get(f"{API_BASE}/events?status=active&page_size=10")
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! Found {len(data.get('items', []))} active events")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Get admin applications
    print("\n5. Testing GET /personas/admin/verifications (admin)...")
    try:
        resp = requests.get(
            f"{API_BASE}/personas/admin/verifications?status_filter=pending",
            auth=HTTPBasicAuth(ADMIN_USER, ADMIN_PASS)
        )
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! Found {len(data.get('items', []))} pending applications")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*50)
    print("✅ API Test Complete!")
    print("\nNext: Open http://localhost:3002/personas in browser")
    print("Flow: Create Persona → Apply for Verification → Admin Review")

if __name__ == "__main__":
    try:
        test_persona_system()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the backend running on port 8080?")
        print("   Run: cd wrhitw/apps/api && ./venv/bin/uvicorn app.main:app --reload --port 8080")
