from app.db.mongo.helper import MongoHelper
from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

class TransactionService:

    @staticmethod
    async def get_all_transactions_admin(
        limit: int,
        skip: int,
        status: str = None,
    ):
        """
        Get all Telegram bot transactions for admin with optional status filter.
        """
        try:
            logger.info(f"Fetching transactions with limit={limit}, skip={skip}, status={status}")

            query = {}
            if status:
                query["status"] = status  # e.g. 'OPEN' or 'CLOSED'
            
            transactions = await MongoHelper.find_many(
                collection=settings.DB_TABLE.TRANSACTIONS,
                query=query,
                projection={"_id": 0},
                limit=limit,
                skip=skip,
                sort=[("updated_at", -1)]
            )

            if not transactions:
                logger.warning(f"No transactions found with criteria status={status}, skip={skip}, limit={limit}")
                return {
                    "status": "success",
                    "status_code": 200,
                    "comment": "No transactions found in given criteria",
                    "data": []
                }
            
            logger.info(f"Number of transactions fetched: {len(transactions)}")
            return {
                "status": "success",
                "status_code": 200,
                "comment": "Transactions fetched successfully",
                "data": transactions or []
            }

        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "status_code": 500,
                "comment": "Internal server error while fetching transactions",
                "data": []
            }

    @staticmethod
    async def get_transaction_by_uuid(transaction_uuid: str):
        """
        Get a single transaction by UUID for admin.
        """
        try:
            logger.info(f"Fetching transaction by uuid: {transaction_uuid}")
            transaction = await MongoHelper.find_many(
                collection=settings.DB_TABLE.TRANSACTIONS,
                query={"uuid": transaction_uuid},
                projection={"_id": 0},
                limit=1
            )
            if not transaction:
                logger.warning(f"Transaction not found for uuid: {transaction_uuid}")
                return {
                    "status": "error",
                    "status_code": 404,
                    "comment": "Transaction not found",
                    "data": {}
                }
            transaction = transaction[0]

            logger.info(f"Transaction fetched successfully for uuid: {transaction_uuid}")
            return {
                "status": "success",
                "status_code": 200,
                "comment": "Transaction fetched successfully",
                "data": transaction
            }
        except Exception as e:
            logger.error(f"Error fetching transaction by uuid: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "status_code": 500,
                "comment": "Internal server error while fetching transaction",
                "data": {}
            }

    @staticmethod
    async def get_transactions_by_user(user_id: str, limit: int = 10, skip: int = 0):
        """
        Get transactions for a specific user by user_id.
        """
        try:
            logger.info(f"Fetching transactions for user_id: {user_id} with limit={limit}, skip={skip}")
            transactions = await MongoHelper.find_many(
                collection=settings.DB_TABLE.TRANSACTIONS,
                query={"user_id": user_id},
                projection={"_id": 0},
                limit=limit,
                skip=skip,
                sort=[("updated_at", -1)]
            )

            if not transactions:
                logger.warning(f"No transactions found for user_id: {user_id}")
                return {
                    "status": "success",
                    "status_code": 200,
                    "comment": "No transactions found for the user",
                    "data": []
                }

            logger.info(f"Number of transactions fetched for user_id {user_id}: {len(transactions)}")
            return {
                "status": "success",
                "status_code": 200,
                "comment": "User transactions fetched successfully",
                "data": transactions or []
            }
        except Exception as e:
            logger.error(f"Error fetching transactions for user_id {user_id}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "status_code": 500,
                "comment": "Internal server error while fetching user transactions",
                "data": []
            }