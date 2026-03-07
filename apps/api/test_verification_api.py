#!/usr/bin/env python3
"""
Quick test script to verify stakeholder verification system
"""

import requests
from requests.auth import HTTPBasicAuth

API_BASE = "http://localhost:8080/api"

# Test credentials
USER_EMAIL = "test@example.com"
USER_PASS = "test123"
ADMIN_USER = "admin"
ADMIN_PASS = "wrhitw_admin_2026"

def test_api():
    print("🧪 Testing Stakeholder Verification System\n")
    
    # Test 1: Get stakeholders (public)
    print("1. Testing GET /stakeholders/list (public)...")
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
    
    # Test 2: Get my applications (user)
    print("\n2. Testing GET /stakeholders/my-applications...")
    try:
        resp = requests.get(
            f"{API_BASE}/stakeholders/my-applications",
            auth=HTTPBasicAuth(USER_EMAIL, USER_PASS)
        )
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! User has {len(data.get('items', []))} applications")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get admin applications
    print("\n3. Testing GET /stakeholders/admin/applications...")
    try:
        resp = requests.get(
            f"{API_BASE}/stakeholders/admin/applications",
            auth=HTTPBasicAuth(ADMIN_USER, ADMIN_PASS)
        )
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! Found {len(data.get('items', []))} applications")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get my roles
    print("\n4. Testing GET /stakeholders/my-roles...")
    try:
        resp = requests.get(
            f"{API_BASE}/stakeholders/my-roles",
            auth=HTTPBasicAuth(USER_EMAIL, USER_PASS)
        )
        if resp.ok:
            data = resp.json()
            print(f"   ✅ Success! User has {len(data.get('items', []))} verified roles")
        else:
            print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*50)
    print("✅ API Test Complete!")
    print("\nNext: Open http://localhost:3001/verify in browser")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the backend running on port 8080?")
        print("   Run: cd wrhitw/apps/api && ./venv/bin/uvicorn app.main:app --reload --port 8080")
