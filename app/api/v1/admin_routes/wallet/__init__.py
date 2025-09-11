from fastapi import APIRouter
from .wallet import router as wallet_router

router = APIRouter(prefix="/wallet", tags=["wallet"])

router.include_router(wallet_router)