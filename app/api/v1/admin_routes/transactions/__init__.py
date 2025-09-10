from fastapi import APIRouter
from .transactions import router as transaction_router

router = APIRouter(prefix="/transactions", tags=["Transactions"])

router.include_router(transaction_router)