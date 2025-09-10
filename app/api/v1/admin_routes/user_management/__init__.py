from fastapi import APIRouter
from .user_management import router as user_management_router

router = APIRouter(prefix="/user-management", tags=["User Management"])

router.include_router(user_management_router)