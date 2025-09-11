from fastapi import APIRouter
from .auth import router as auth_router
from .user_management import router as user_router
from .transactions import router as transaction_router
from .wallet import router as wallet_router

router = APIRouter(
    prefix="/admin",
)

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(transaction_router)
router.include_router(wallet_router)