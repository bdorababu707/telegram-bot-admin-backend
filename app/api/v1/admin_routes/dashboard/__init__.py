from fastapi import APIRouter, Depends
from .dashboard import router as dashboard_router

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

router.include_router(dashboard_router)