from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..services import keycloak_admin
import os

router = APIRouter(prefix="/otp-stub", tags=["otp-stub"])

# Simple in-memory OTP store: phone -> {otp, expires_at}
otp_store: dict = {}


class OTPRequestIn(BaseModel):
    phone_number: str


@router.post("/request")
async def otp_request(data: OTPRequestIn):
    phone = data.phone_number
    user = await keycloak_admin.find_user_by_username(phone)
    if not user:
        user = await keycloak_admin.create_user(phone, None, None, phone, "customer")
    otp = "%06d" % (int(datetime.utcnow().timestamp()) % 1000000)
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    otp_store[phone] = {"otp": otp, "expires_at": expires_at}
    await keycloak_admin.set_user_password(user.get("id"), otp)
    print(f"OTP for {phone}: {otp}")
    if os.getenv("DEBUG_RETURN_OTP", "false").lower() in ("1", "true", "yes"):
        return {"status": "ok", "otp": otp}
    return {"status": "ok"}


class OTPVerifyIn(BaseModel):
    phone_number: str
    otp: str


@router.post("/verify")
async def otp_verify(data: OTPVerifyIn):
    entry = otp_store.get(data.phone_number)
    if not entry or entry.get("otp") != data.otp or entry.get("expires_at") < datetime.utcnow():
        return {"status": "error", "detail": "Invalid or expired OTP"}
    return {"status": "ok"}
