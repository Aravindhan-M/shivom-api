from functools import lru_cache
from typing import Any, Optional

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from ..config import Settings
from ..database import get_async_session
from sqlalchemy import select
from ..models.user_profile import UserProfile

settings = Settings()
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def _validate_client_audience(payload: dict[str, Any]) -> None:
    if not settings.KEYCLOAK_CLIENT_ID:
        return

    azp = payload.get("azp")
    aud = payload.get("aud")
    aud_valid = False
    if isinstance(aud, str):
        aud_valid = aud == settings.KEYCLOAK_CLIENT_ID
    elif isinstance(aud, list):
        aud_valid = settings.KEYCLOAK_CLIENT_ID in aud

    if azp != settings.KEYCLOAK_CLIENT_ID and not aud_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience")


@lru_cache()
def _get_jwks_client():
    jwks_url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    return PyJWKClient(jwks_url)


async def decode_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=settings.KEYCLOAK_ISSUER,
            options={"verify_aud": False},
        )
        _validate_client_audience(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception as e:
        print(f"TOKEN DECODE ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_optional_payload(credentials: Optional[HTTPAuthorizationCredentials] = Security(optional_security)) -> Optional[dict]:
    if not credentials:
        return None
    token = credentials.credentials
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=settings.KEYCLOAK_ISSUER,
            options={"verify_aud": False},
        )
        _validate_client_audience(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception as e:
        print(f"OPTIONAL TOKEN DECODE ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_role(required_role: str):
    async def _dependency(payload: dict = Depends(decode_token)):
        roles = payload.get("realm_access", {}).get("roles", [])
        if required_role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return payload

    return _dependency


def require_any_role(*roles_expected: str):
    async def _dependency(payload: dict = Depends(decode_token)):
        roles = payload.get("realm_access", {}).get("roles", [])
        for r in roles_expected:
            if r in roles:
                return payload
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    return _dependency


async def get_current_user_profile(payload: dict = Depends(decode_token), db=Depends(get_async_session)) -> UserProfile:
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing sub in token")
    q = await db.execute(select(UserProfile).where(UserProfile.keycloak_sub == sub))
    user = q.scalar_one_or_none()
    if user:
        return user
    # create user profile
    role = "customer"
    roles = payload.get("realm_access", {}).get("roles", [])
    for r in ("admin", "business", "customer"):
        if r in roles:
            role = r
            break
    user = UserProfile(
        keycloak_sub=sub,
        role=role,
        full_name=payload.get("name") or payload.get("preferred_username"),
        email=payload.get("email"),
        phone_number=payload.get("phone_number") or payload.get("phone"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
