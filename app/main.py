from fastapi import FastAPI, Depends

from app.core.security import (
    get_current_user,
    require_role
)

# Database
from app.db.database import engine
from app.db.base import Base

# Models
from app.models.user import User
from app.models.category import Category
from app.models.business import Business
from app.models.business_media import BusinessMedia
from app.models.offer import Offer
from app.models.receipt import Receipt
from app.models.reward import RewardTransaction
from app.models.referral import Referral

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WINGS API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "WINGS API Running"
    }


@app.get("/profile")
async def profile(
        user=Depends(get_current_user)
):
    return user


@app.get("/admin")
async def admin(
        user=Depends(require_role("admin"))
):
    return {
        "message": "Admin Access"
    }


@app.get("/business")
async def business(
        user=Depends(require_role("business"))
):
    return {
        "message": "Business Access"
    }


@app.get("/customer")
async def customer(
        user=Depends(require_role("customer"))
):
    return {
        "message": "Customer Access"
    }


@app.get("/health/db")
def db_health():
    return {
        "message": "Database Connected"
    }