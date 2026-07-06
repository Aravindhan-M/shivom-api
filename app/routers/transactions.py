from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session
from ..deps.auth import require_role, decode_token
from ..models.business import Business
from ..models.receipt import Receipt
from ..models.reward import Reward
from ..models.referral import Referral
from ..services.audit import log_audit

router = APIRouter(tags=["transactions"])

class ReceiptCreate(BaseModel):
    business_id: str
    amount: float
    receipt_date: datetime

class ReceiptProcess(BaseModel):
    remarks: Optional[str] = None

class ReferralCreate(BaseModel):
    referral_code: str

@router.post("/receipts", status_code=status.HTTP_201_CREATED)
async def create_receipt(data: ReceiptCreate, payload: dict = Depends(require_role("customer")), db: AsyncSession = Depends(get_async_session)):
    receipt = Receipt(
        customer_sub=payload.get("sub"),
        business_id=data.business_id,
        amount=data.amount,
        receipt_date=data.receipt_date,
        status="pending",
    )
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)
    await log_audit(
        db,
        payload.get("sub"),
        ",".join(payload.get("realm_access", {}).get("roles", [])),
        "CREATE_RECEIPT",
        "receipt",
        str(receipt.id),
        None,
    )
    return {"id": str(receipt.id), "status": receipt.status}

@router.patch("/receipts/{id}/approve")
async def approve_receipt(id: str, payload: dict = Depends(require_role("business")), db: AsyncSession = Depends(get_async_session)):
    stmt = select(Receipt).where(Receipt.id == id)
    result = await db.execute(stmt)
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    business = await db.get(Business, receipt.business_id)
    if not business or business.owner_sub != payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    receipt.status = "approved"
    reward = Reward(customer_sub=receipt.customer_sub, receipt_id=receipt.id, points=int(receipt.amount * 0.1), reason="Receipt verified")
    db.add(reward)
    await db.commit()
    await log_audit(
        db,
        payload.get("sub"),
        ",".join(payload.get("realm_access", {}).get("roles", [])),
        "APPROVE_RECEIPT",
        "receipt",
        str(receipt.id),
        None,
    )
    return {"status": "approved"}

@router.patch("/receipts/{id}/reject")
async def reject_receipt(id: str, reject: ReceiptProcess, payload: dict = Depends(require_role("business")), db: AsyncSession = Depends(get_async_session)):
    stmt = select(Receipt).where(Receipt.id == id)
    result = await db.execute(stmt)
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    business = await db.get(Business, receipt.business_id)
    if not business or business.owner_sub != payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    receipt.status = "rejected"
    receipt.remarks = reject.remarks
    receipt.reviewed_by = payload.get("sub")
    receipt.reviewed_at = datetime.utcnow()
    await db.commit()
    await log_audit(
        db,
        payload.get("sub"),
        ",".join(payload.get("realm_access", {}).get("roles", [])),
        "REJECT_RECEIPT",
        "receipt",
        str(receipt.id),
        {"remarks": reject.remarks},
    )
    return {"status": "rejected"}

@router.get("/rewards/me")
async def rewards_me(payload: dict = Depends(require_role("customer")), db: AsyncSession = Depends(get_async_session)):
    stmt = select(Reward).where(Reward.customer_sub == payload.get("sub"))
    result = await db.execute(stmt)
    rewards = result.scalars().all()
    return [
        {"id": str(r.id), "receipt_id": str(r.receipt_id) if r.receipt_id else None, "points": r.points, "reason": r.reason, "created_at": r.created_at}
        for r in rewards
    ]

@router.get("/rewards/summary")
async def rewards_summary(payload: dict = Depends(require_role("customer")), db: AsyncSession = Depends(get_async_session)):
    stmt = select(Reward).where(Reward.customer_sub == payload.get("sub"))
    result = await db.execute(stmt)
    rewards = result.scalars().all()
    total_points = sum(r.points for r in rewards)
    return {"total_points": total_points, "total_rewards": len(rewards)}

@router.post("/referrals", status_code=status.HTTP_201_CREATED)
async def create_referral(data: ReferralCreate, payload: dict = Depends(require_role("customer")), db: AsyncSession = Depends(get_async_session)):
    referral = Referral(referrer_sub=payload.get("sub"), referral_code=data.referral_code)
    db.add(referral)
    await db.commit()
    await db.refresh(referral)
    await log_audit(
        db,
        payload.get("sub"),
        ",".join(payload.get("realm_access", {}).get("roles", [])),
        "CREATE_REFERRAL",
        "referral",
        str(referral.id),
        None,
    )
    return {"id": str(referral.id), "status": referral.status}

@router.get("/referrals/me")
async def referrals_me(payload: dict = Depends(require_role("customer")), db: AsyncSession = Depends(get_async_session)):
    stmt = select(Referral).where(Referral.referrer_sub == payload.get("sub"))
    result = await db.execute(stmt)
    referrals = result.scalars().all()
    return [
        {"id": str(r.id), "referred_sub": r.referred_sub, "referral_code": r.referral_code, "status": r.status, "points_awarded": r.points_awarded, "created_at": r.created_at}
        for r in referrals
    ]
