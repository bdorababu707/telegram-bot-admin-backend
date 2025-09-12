from fastapi import APIRouter, Depends
from app.utils.security import get_current_admin
from app.services.dashboard import DashboardService
from app.models.base import OutModel

router = APIRouter()

@router.get("/overview", response_model=OutModel)
async def get_admin_overview(current_admin: str = Depends(get_current_admin)):
    try:
        return await DashboardService.get_admin_overview()
    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment="Internal server error while fetching admin overview",
            data=""
        )
