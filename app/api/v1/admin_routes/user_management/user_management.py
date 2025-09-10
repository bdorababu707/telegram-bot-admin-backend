from fastapi import APIRouter, Query, Depends, Path, HTTPException, Body
from app.services.user_management import AdminUserService
from app.models.base import OutModel
from app.utils.security import get_current_admin
from typing import Optional,Literal

router = APIRouter()

@router.get("/user/user-name", tags=["User Management"])
async def get_user_details(
    username: str = Query(..., description="Username of the user to fetch details for"),
    current_admin=Depends(get_current_admin)
):
    
    try:
        response = await AdminUserService.get_user_details(username)
        return response
    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Failed to get user details",
            data=str(e)
        )

