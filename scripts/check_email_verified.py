import asyncio
import os
import time
import json
import sys

# ensure project root is on PYTHONPATH when running inside container
sys.path.append(os.getcwd())
from app.services import keycloak_admin
from app.services.keycloak_admin import settings as kc_settings
import httpx

async def main():
    ts = int(time.time())
    phone = f"999_check_{ts}"
    print("Creating user", phone)
    user = await keycloak_admin.create_user(phone, None, None, phone, "customer", password="TestPass123!")
    print("Created user, querying...")
    found = await keycloak_admin.find_user_by_username(phone)
    print(json.dumps(found, indent=2))
    user_id = found.get("id")
    if user_id:
        token = await keycloak_admin.get_admin_token()
        url = f"{kc_settings.KEYCLOAK_SERVER_URL}/admin/realms/{kc_settings.KEYCLOAK_REALM}/users/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as c:
            r = await c.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            full = r.json()
        print("Full user JSON:")
        print(json.dumps(full, indent=2))
        print("emailVerified:", full.get("emailVerified"))
        print("requiredActions:", full.get("requiredActions"))

if __name__ == '__main__':
    asyncio.run(main())
