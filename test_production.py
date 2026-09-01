#!/usr/bin/env python3
"""Test production endpoints to diagnose the 500 error."""

import httpx
import json
import time

BASE_URL = "https://finance-advisor-ai-1.onrender.com"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Test backend health endpoints."""
    print("=" * 60)
    print("TESTING HEALTH ENDPOINTS")
    print("=" * 60)
    
    try:
        r = httpx.get(f"{BASE_URL}/health", timeout=10)
        print(f"✓ Health endpoint: {r.status_code}")
        print(f"  Response: {r.text}")
    except Exception as e:
        print(f"✗ Health error: {e}")
    
    try:
        r = httpx.get(f"{API_BASE}/health", timeout=10)
        print(f"✓ API Health endpoint: {r.status_code}")
        print(f"  Response: {r.text}")
    except Exception as e:
        print(f"✗ API Health error: {e}")


def test_register():
    """Test registration endpoint."""
    print("\n" + "=" * 60)
    print("TESTING REGISTER ENDPOINT")
    print("=" * 60)
    
    # Generate unique email
    email = f"test-{int(time.time())}-{hash('test') % 10000}@example.com"
    payload = {
        "full_name": "Test User",
        "email": email,
        "password": "Test@12345"
    }
    
    print(f"Registering with email: {email}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        r = httpx.post(
            f"{API_BASE}/auth/register",
            json=payload,
            timeout=10
        )
        print(f"\n✓ Status Code: {r.status_code}")
        print(f"Response Headers:")
        for k, v in r.headers.items():
            print(f"  {k}: {v}")
        print(f"Response Body:")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_login():
    """Test login endpoint."""
    print("\n" + "=" * 60)
    print("TESTING LOGIN ENDPOINT")
    print("=" * 60)
    
    payload = {
        "email": "test@example.com",
        "password": "wrong_password"
    }
    
    print(f"Login payload: {json.dumps(payload, indent=2)}")
    
    try:
        r = httpx.post(
            f"{API_BASE}/auth/login",
            json=payload,
            timeout=10
        )
        print(f"\n✓ Status Code: {r.status_code}")
        print(f"Response:")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    test_health()
    test_register()
    test_login()
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
