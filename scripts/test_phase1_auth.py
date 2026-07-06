import os
import sys
import time
import httpx

BASE = os.getenv("BASE_URL", "http://localhost:8000")

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

def ok(msg):
    print("PASS:", msg)

def main():
    ts = int(time.time())
    phone = f"999{ts}"
    password = f"Pass{ts}!"
    register_payload = {"phone_number": phone, "full_name": "Test User", "role": "customer", "password": password}
    with httpx.Client(timeout=10.0) as c:
        # Register
        r = c.post(f"{BASE}/auth/register", json=register_payload)
        if r.status_code != 201:
            fail(f"register failed: {r.status_code} {r.text}")
        ok("register")
        # Login with password
        r = c.post(f"{BASE}/auth/login", json={"username": phone, "password": password})
        if r.status_code != 200:
            fail(f"login failed: {r.status_code} {r.text}")
        tokens = r.json()
        access = tokens.get("access_token")
        if not access:
            fail("no access token returned from login")
        ok("login and token issuance")

        # Call /auth/me
        headers = {"Authorization": f"Bearer {access}"}
        r = c.get(f"{BASE}/auth/me", headers=headers)
        if r.status_code != 200:
            fail(f"auth me failed: {r.status_code} {r.text}")
        j = r.json()
        profile = j.get("profile")
        if not profile or profile.get("phone_number") != phone:
            fail(f"profile mismatch: {j}")
        ok("auth me returned profile")

        # Test role: admin endpoint should be forbidden for customer
        r = c.get(f"{BASE}/auth/test-role/admin", headers=headers)
        if r.status_code != 403:
            fail(f"test-role expected 403, got {r.status_code} {r.text}")
        ok("test-role forbidden for customer")

    print("ALL STEPS PASSED")

if __name__ == '__main__':
    main()
