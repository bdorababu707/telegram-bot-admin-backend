from typing import Any, Dict, Optional
from app.db.mongo.helper import MongoHelper
from app.models.base import OutModel
from app.utils.logging import get_logger
from app.utils.config import settings
import time

logger = get_logger(__name__)


class AdminUserService:

    @staticmethod
    async def get_all_users(
        limit: int,
        skip: int,
        status: Optional[str] = None,
    ) -> OutModel:
        
        """
        Get all users with optional filters for status.
        """
        try:
            logger.info(f"Fetching users with limit={limit}, skip={skip}, status={status}")

            query = {}
            if status:
                query["status"] = status  # e.g. 'ACTIVE', 'SUSPENDED'

            users = await MongoHelper.find_many(
                collection=settings.DB_TABLE.USERS,
                query=query,
                projection={"_id": 0, "password": 0},  # Exclude sensitive fields
                limit=limit,
                skip=skip,
                sort=[("created_at", -1)]
            )

            if not users:
                logger.warning(f"No users found with criteria status={status}, skip={skip}, limit={limit}")
                return OutModel(
                    status="success",
                    status_code=200,
                    comment="No users found in given criteria",
                    data=[]
                )

            logger.info(f"Number of users fetched: {len(users)}")
            return OutModel(
                status="success",
                status_code=200,
                comment="Users fetched successfully",
                data=users or []
            )

        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}", exc_info=True)
            return OutModel(
                status="error",
                status_code=500,
                comment="Internal server error while fetching users",
                data=[]
            )
    
    @staticmethod
    async def get_user_details(phone_number: str) -> dict:
        try:
            # Get user document
            logger.info(f"Fetching user details for phone number: {phone_number}")
            user = await MongoHelper.find_one(
                collection=settings.DB_TABLE.USERS, 
                query={"phone_number": phone_number},
                projection={"_id": 0}
            )
            if not user:
                logger.warning(f"User not found with phone number: {phone_number}")
                return {
                    "status": "error",
                    "status_code": 404,
                    "comment": "User not found",
                    "data": ""
                }

            # Get wallet balance
            wallet = await MongoHelper.find_one(settings.DB_TABLE.WALLETS, {"user_id": user.get("uuid")})
            wallet_balance = wallet.get("balance") if wallet else 0.0

            # Get gold holdings
            # inventory = await MongoHelper.find_one(settings.DB_TABLE.INVENTORY, {"user_id": user_id})
            # gold_holdings = inventory.get("gold_balance") if inventory else 0.0

            logger.info(f"User details fetched for phone number: {phone_number}")
            return {
                "status": "success",
                "status_code": 200,
                "comment": "User details fetched successfully",
                "data": {
                    'user': user,
                    'wallet_balance': wallet_balance,
                }
            }
        except Exception as e:
            logger.error(f"Error in get_user_details by phone number: {phone_number}, error: {e}")
            return {
                "status": "error",
                "status_code": 500,
                "comment": "Failed to fetch user details",
                "data": str(e)
            }

    @staticmethod
    async def update_user_status(user_id: str, admin: dict) -> OutModel:
        try:

            logger.info(f"Admin {admin.get('uuid')} is updating user {user_id} status.")
            # Fetch existing user
            user = await MongoHelper.find_one(settings.DB_TABLE.USERS, {"uuid": user_id})
            if not user:
                logger.warning(f"User not found: {user_id}")
                return OutModel(
                    status="success",
                    status_code=404,
                    comment="User not found or status not updated",
                    data=""
                )
            
            result = await MongoHelper.update_one(
                settings.DB_TABLE.USERS, 
                {"uuid": user_id}, 
                {"$set": {"status": "APPROVED", "updated_at": int(time.time()), "metadata": {"approved_by": admin.get("uuid"), "approved_at": int(time.time())}}}
            )

            if result > 0:
                logger.info(f"Successfully updated user {user_id} status to APPROVED.")
                return OutModel(
                    status="success",
                    status_code=200,
                    comment=f"User status updated to APPROVED",
                    data={"user_id": user_id, "new_status": "APPROVED"}
                )
            else:
                logger.warning(f"Update failed for user {user_id}.")
                return OutModel(
                    status="success",
                    status_code=404,
                    comment="User not found or status not updated",
                    data=""
                )
            
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
            return OutModel(
                status="error",
                status_code=500,
                comment="Failed to update user status",
                data=str(e)
            )

    @staticmethod
    async def get_user_by_id(user_id: str) -> OutModel:
        try:
            user = await MongoHelper.find_one(
                collection=settings.DB_TABLE.USERS,
                query={"uuid": user_id},
                projection={"_id": 0, "password": 0}  # Exclude sensitive fields
            )
            if not user:
                logger.warning(f"User not found with ID: {user_id}")
                return OutModel(
                    status="error",
                    status_code=404,
                    comment="User not found",
                    data=""
                )

            logger.info(f"User fetched successfully with ID: {user_id}")
            return OutModel(
                status="success",
                status_code=200,
                comment="User fetched successfully",
                data=user
            )

        except Exception as e:
            logger.error(f"Error fetching user by ID: {str(e)}", exc_info=True)
            return OutModel(
                status="error",
                status_code=500,
                comment="Internal server error while fetching user",
                data=""
            )

    @staticmethod
    async def get_user_overview(user_id: str) -> OutModel:
        try:
            logger.info(f"Fetching overview for user_id: {user_id}")

            # Fetch user details
            logger.info(f"Fetching user details for user_id: {user_id}")
            user = await MongoHelper.find_one(settings.DB_TABLE.USERS, {"uuid": user_id}, projection={"_id": 0})
            if not user:
                logger.warning(f"User not found for user_id: {user_id}")
                return OutModel(
                    status="error",
                    status_code=404,
                    comment="User not found",
                    data=""
                )

            # Fetch wallet details
            logger.info(f"Fetching wallet for user_id: {user_id}")
            wallet = await MongoHelper.find_one(settings.DB_TABLE.WALLETS, {"user_id": user_id}, projection={"_id": 0}) or {}

            # Fetch transactions (all: buy, sell, closed)
            logger.info(f"Fetching transactions for user_id: {user_id}")
            transactions = await MongoHelper.find_many(settings.DB_TABLE.TRANSACTIONS, {"user_id": user_id}, projection={"_id": 0}, sort=[("created_at", -1)]) or []

            response: Dict[str, Any] = {
                "user": user,
                "wallet": wallet,
                "transactions": transactions,
            }
            
            logger.info(f"User dashboard fetched successfully for user_id: {user_id}")
            return OutModel(
                status="success",
                status_code=200,
                comment="User dashboard fetched successfully",
                data=response
            )

        except Exception as e:
            logger.error(f"Error fetching user dashboard for {user_id}: {str(e)}")
            return OutModel(
                status="error",
                status_code=500,
                comment="Failed to fetch user dashboard",
                data=str(e)
            )