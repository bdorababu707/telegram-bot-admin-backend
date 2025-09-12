from fastapi import APIRouter, Query, Depends, Path, HTTPException, Body
from app.services.user_management import AdminUserService
from app.models.base import OutModel
from app.utils.security import get_current_admin
from typing import Optional,Literal

router = APIRouter()

@router.get("/user/phone-number")
async def get_user_details(
    phone_number: str = Query(..., description="Phone number of the user to fetch details for"),
    current_admin=Depends(get_current_admin)
):
    
    try:
        response = await AdminUserService.get_user_details(phone_number)
        return response
    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Failed to get user details",
            data=str(e)
        )

@router.get("/user/id")
async def get_user_by_id(user_id: str = Query(..., description="Id of the user"),
    current_admin=Depends(get_current_admin)
    ):
    try:
        user = await AdminUserService.get_user_by_id(user_id)
        return user

    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Internal server error while fetching user details",
            data=""
        )


@router.get("/all-users")
async def get_all_users(
    status: Literal["APPROVED", "PENDING"] = None,
    limit: int = Query(10, ge=1, le=1000, description="Number of users to return"),
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    current_admin=Depends(get_current_admin)
):
    try:
        response = await AdminUserService.get_all_users(status=status, limit=limit, skip=skip)
        return response
    
    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Internal server error while fetching users",
            data=""
        )

@router.patch("/approve-user")
async def update_user_status(
    user_id: str = Query(..., description="ID of the user to update"),
    current_admin=Depends(get_current_admin)
):
    try:
        response = await AdminUserService.update_user_status(user_id=user_id, admin=current_admin)
        return response
    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Failed to update user status",
            data=str(e)
        )   