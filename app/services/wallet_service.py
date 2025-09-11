from app.schemas.wallet import AddFundsRequest
from app.utils.config import settings
from app.utils.logging import get_logger
from app.models.base import OutModel
from app.db.mongo.helper import MongoHelper
import time

logger = get_logger(__name__)

class WalletService:
    @staticmethod
    async def add_funds_to_wallet(data: AddFundsRequest, admin: dict) -> OutModel:
        try:
            user_id = data.user_id
            amount = data.amount

            logger.info(f"Admin {admin.get('email')} is adding {amount} to wallet of user_id {user_id}")
            if amount <= 0:
                logger.warning(f"Invalid amount {amount} provided by admin {admin.get('email')} for user_id {user_id}")
                return OutModel(
                    status="error",
                    status_code=400,
                    comment="Amount must be greater than zero",
                    data=None
                )

            # Fetch existing wallet or create a new one
            wallet = await MongoHelper.find_one(settings.DB_TABLE.WALLETS, {"user_id": user_id})
            if not wallet:
                logger.info(f"Wallet not found for user_id {user_id}")
                return OutModel(
                    status="error",
                    status_code=404,
                    comment="Wallet not found for the given user_id",
                    data=None
                )
            
            # Update wallet balance
            new_balance = wallet["balance"] + amount
            await MongoHelper.update_one(
                settings.DB_TABLE.WALLETS,
                {"user_id": user_id},
                {"$set": {"balance": new_balance, "updated_at": time.time()}}
            )

            # Log the transaction
            transaction = {
                'user_id': user_id,
                'status': 'SUCCESS',
                'created_at': time.time(),
                'updated_at': time.time(),
                'transaction_reference': f'TXN_{int(time.time())}_{user_id[:8]}',
                'metadata': {
                    'wallet_id': wallet['uuid'],
                    'previous_balance': wallet['balance'],
                    'payment_method': 'ADMIN_ADD_FUND',
                },
                'amount': amount,
                'currency': data.currency,
                'payment_method':data.payment_method,
            }
            await MongoHelper.insert_one(collection=settings.DB_TABLE.WALLET_TRANSACTIONS, document=transaction)

            return OutModel(
                status="success",
                status_code=200,
                comment="Funds added to wallet successfully",
                data={"new_balance": new_balance}
            )

        except Exception as e:
            logger.error(f"Error adding funds to wallet for user_id {user_id}: {str(e)}", exc_info=True)
            return OutModel(
                status="error",
                status_code=500,
                comment="Internal server error while adding funds to wallet",
                data=str(e)
            )
        
    @staticmethod
    async def get_user_wallet(user_id: str) -> OutModel:
        try:
            logger.info(f"Fetching wallet for user_id {user_id}")

            wallet = await MongoHelper.find_one(settings.DB_TABLE.WALLETS, {"user_id": user_id}, projection={"_id": 0})
            if not wallet:
                logger.warning(f"Wallet not found for user_id {user_id}")
                return OutModel(
                    status="error",
                    status_code=404,
                    comment="Wallet not found for the given user_id",
                    data=None
                )

            logger.info(f"Wallet fetched successfully for user_id {user_id}")
            return OutModel(
                status="success",
                status_code=200,
                comment="Wallet retrieved successfully",
                data=wallet
            )

        except Exception as e:
            logger.error(f"Error retrieving wallet for user_id {user_id}: {str(e)}", exc_info=True)
            return OutModel(
                status="error",
                status_code=500,
                comment="Internal server error while retrieving wallet",
                data=str(e)
            )