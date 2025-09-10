from fastapi import APIRouter, Query, Depends
from app.schemas.admin import CreateSuperAdmin, CreateAdmin, AdminLoginRequest
from app.services.admin_service import AdminService
from app.utils.logging import get_logger
from app.utils.security import get_current_admin
from app.models.base import OutModel

logger = get_logger(__name__)
router = APIRouter()


@router.post("/create-super-admin", response_model=OutModel)
async def create_super_admin(
    payload: CreateSuperAdmin,
    secret_key: str = Query(..., description="Secret key for Super Admin creation"),
):
    """
    Create a Super Admin.
    """
    try:
        result = await AdminService.create_super_admin(payload, secret_key)
        return result
    except Exception as e:
        logger.exception(f"Error while creating super admin : {str(e)}")
        return OutModel(
            status="error",
            status_code=500,
            comment="Failed to create super admin",
            data=str(e),
        )

@router.post("/create-admin", response_model=OutModel)
async def create_admin(
    payload: CreateAdmin,
    current_admin: dict = Depends(get_current_admin),
):
    try:
        return await AdminService.create_admin_service(current_admin, payload)
    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Failed to create admin",
            data=str(e),
        )
    
@router.get("/me", response_model=OutModel)
async def get_current_admin_profile(current_admin: dict = Depends(get_current_admin)):
    try:
        return await AdminService.get_current_user_details(current_admin)
    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Failed to get current admin profile",
            data=str(e),
        )
    
@router.post("/login", response_model=OutModel)
async def admin_login(payload: AdminLoginRequest):
    try:
        return await AdminService.admin_login(
            email=payload.email, password=payload.password
        )
    except Exception as e:
        logger.exception(f"Unexpected error while logging in admin : {str(e)}")
        return OutModel(
            status="error",
            status_code=500,
            comment="Internal server error",
            data=None,
        )