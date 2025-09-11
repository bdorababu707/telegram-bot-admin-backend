from fastapi import APIRouter, Depends, Query
from app.utils.security import get_current_admin
from app.services.transaction_service import TransactionService
from app.models.base import OutModel

router = APIRouter()

@router.get("/get-transactions", response_model=OutModel)
async def admin_get_transactions(
    status: str = Query(None, enum=["OPEN", "CLOSED"]),
    skip: int = Query(0),
    limit: int = Query(10),
    current_admin: dict = Depends(get_current_admin)
):
    try:
        response = await TransactionService.get_all_transactions_admin(
            status=status,
            skip=skip,
            limit=limit
        )
        return OutModel(**response)

    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment=f"Failed to fetch transactions: {str(e)}",
            data=[]
        )

@router.get("/get-transaction/id", response_model=OutModel)
async def admin_get_transaction_by_id(
    transaction_id: str = Query(..., description="UUID of the transaction"),
    current_admin: dict = Depends(get_current_admin)
):
    try:
        response = await TransactionService.get_transaction_by_uuid(transaction_id)
        return OutModel(**response)

    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment=f"Failed to fetch transaction: {str(e)}",
            data=[]
        )
    
@router.get("/get-transaction/user-id", response_model=OutModel)
async def admin_get_transactions_by_user_id(
    user_id: str = Query(..., description="User ID to fetch transactions for"),
    limit: int = Query(10, description="Number of records to fetch"),
    skip: int = Query(0, description="Number of records to skip"),
    current_admin: dict = Depends(get_current_admin)
):
    try:
        response = await TransactionService.get_transactions_by_user(
            user_id=user_id,
            limit=limit,
            skip=skip
        )
        return OutModel(**response)

    except Exception as e:
        return OutModel(
            status="error",
            status_code=500,
            comment=f"Failed to fetch transactions for user: {str(e)}",
            data=[]
        )