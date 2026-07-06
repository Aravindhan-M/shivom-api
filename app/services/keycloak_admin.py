import os
from typing import Optional

import httpx

from ..config import Settings

settings = Settings()


async def get_admin_token() -> str:
    token_url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    # Try client_credentials first (if client has service account), otherwise
    # fall back to admin username/password (admin-cli).
    client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    async with httpx.AsyncClient() as c:
        if client_secret:
            data = {
                "grant_type": "client_credentials",
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "client_secret": client_secret,
            }
            r = await c.post(token_url, data=data, timeout=10)
            if r.status_code == 200:
                j = r.json()
                return j["access_token"]
        # fallback to admin credentials
        admin_user = os.getenv("KEYCLOAK_ADMIN", "")
        admin_pass = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "")
        if admin_user and admin_pass and settings.KEYCLOAK_ADMIN_CLIENT_ID:
            data = {
                "grant_type": "password",
                "client_id": settings.KEYCLOAK_ADMIN_CLIENT_ID,
                "username": admin_user,
                "password": admin_pass,
            }
            r2 = await c.post(token_url, data=data, timeout=10)
            r2.raise_for_status()
            j2 = r2.json()
            return j2["access_token"]
        raise RuntimeError("Unable to obtain admin token: no valid method available")


async def find_user_by_username(username: str) -> Optional[dict]:
    token = await get_admin_token()
    url = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users"
    params = {"username": username}
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as c:
        r = await c.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        users = r.json()
        return users[0] if users else None


async def create_user(username: str, email: Optional[str], first_name: Optional[str], phone_number: Optional[str], role: str, password: Optional[str] = None) -> dict:
    token = await get_admin_token()
    url = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users"
    payload = {
        "username": username,
        "email": email if email is not None else "",
        "firstName": first_name,
        "enabled": True,
        "emailVerified": True,
        "requiredActions": [],
        "attributes": {"phone_number": phone_number} if phone_number else {},
    }
    if password:
        payload["credentials"] = [{"type": "password", "value": password, "temporary": False}]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as c:
        r = await c.post(url, json=payload, headers=headers, timeout=10)
        r.raise_for_status()
        # find created user
        return await find_user_by_username(username)


async def set_user_password(user_id: str, password: str) -> None:
    token = await get_admin_token()
    url = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users/{user_id}/reset-password"
    payload = {"type": "password", "temporary": False, "value": password}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as c:
        r = await c.put(url, json=payload, headers=headers, timeout=10)
        r.raise_for_status()


async def assign_realm_role(user_id: str, role: str) -> None:
    token = await get_admin_token()
    # get role representation
    role_url = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/roles/{role}"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as c:
        r = await c.get(role_url, headers=headers, timeout=10)
        r.raise_for_status()
        role_rep = r.json()
        mapping_url = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users/{user_id}/role-mappings/realm"
        r2 = await c.post(mapping_url, json=[role_rep], headers=headers, timeout=10)
        r2.raise_for_status()

async def get_user_by_id(user_id: str) -> dict:
    token = await get_admin_token()
    url = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as c:
        r = await c.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()

async def set_user_enabled(user_id: str, enabled: bool) -> None:
    token = await get_admin_token()
    user = await get_user_by_id(user_id)
    user["enabled"] = enabled
    url = f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as c:
        r = await c.put(url, json=user, headers=headers, timeout=10)
        r.raise_for_status()
