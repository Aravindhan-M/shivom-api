from fastapi import APIRouter, Depends

from ..database import check_db

router = APIRouter()


@router.get("/health")
async def health():
    ok = await check_db()
    if not ok:
        return {"status": "error"}
    return {"status": "ok"}
