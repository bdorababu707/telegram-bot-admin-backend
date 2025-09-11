from fastapi import Depends, FastAPI, APIRouter

from app.models.base import OutModel
from app.schemas.wallet import AddFundsRequest
from app.services.wallet_service import WalletService
from app.utils.security import get_current_admin

router = APIRouter()

@router.post("/add-fund")
async def admin_add_funds_to_wallet(
    data: AddFundsRequest,
    current_admin: dict = Depends(get_current_admin)
):
    try:
        response = await WalletService.add_funds_to_wallet(data, current_admin)
        return response

    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment=f"Failed to add funds: {str(e)}",
            data=None
        )
    
@router.get("/get-user-wallet")
async def get_user_wallet(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    try:
        wallet = await WalletService.get_user_wallet(user_id)

        return wallet

    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment=f"Failed to fetch wallet: {str(e)}",
            data=None
        )