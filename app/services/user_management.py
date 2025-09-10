from typing import Optional
from app.db.mongo.helper import MongoHelper
from app.models.base import OutModel
from app.utils.logging import get_logger
from app.utils.config import settings
import time

logger = get_logger(__name__)


class AdminUserService:
    
    @staticmethod
    async def get_user_details(username: str):
        try:
            # Get user document
            user = await MongoHelper.find_one(
                collection=settings.DB_TABLE.USERS, 
                query={"username": username},
                projection={"_id": 0}
            )
            if not user:
                logger.warning(f"User not found with username: {username}")
                return {
                    "status": "error",
                    "status_code": 404,
                    "comment": "User not found",
                    "data": None
                }

            # Get wallet balance
            wallet = await MongoHelper.find_one(settings.DB_TABLE.WALLETS, {"user_id": user.get("uuid")})
            wallet_balance = wallet.get("balance") if wallet else 0.0

            # Get gold holdings
            # inventory = await MongoHelper.find_one(settings.DB_TABLE.INVENTORY, {"user_id": user_id})
            # gold_holdings = inventory.get("gold_balance") if inventory else 0.0
            
            logger.info(f"User details fetched for username: {username}")
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
            logger.error(f"Error in get_user_details by username: {username}, error: {e}")
            return{
                "status": "error",
                "status_code": 500,
                "comment": "Failed to fetch user details",
                "data": str(e)
            }

    @staticmethod
    async def update_user_status(user_id: str, new_status: str) -> OutModel:
        try:
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
                {"$set": {"status": new_status, "updated_at": int(time.time())}}
            )

            if result > 0:
                logger.info(f"Successfully updated user {user_id} status to '{new_status}'.")
                return OutModel(
                    status="success",
                    status_code=200,
                    comment=f"User status updated to {new_status}",
                    data={"user_id": user_id, "new_status": new_status}
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
    async def get_user_details_service(email: Optional[str], phone_number: Optional[str]) -> dict:
        try:
            if not email and not phone_number:
                logger.warning("User details fetch failed: Email or phone number not provided")
                raise Exception("Either email or phone number is required")

            query = {}
            if email:
                query["email"] = email
            elif phone_number:
                query["phone_number"] = phone_number

            logger.info(f"Fetching user details with query: {query}")
            user = await MongoHelper.find_one(settings.DB_TABLE.USERS, query)

            if not user:
                logger.warning(f"User not found with query: {query}")
                raise Exception("User not found")

            user.pop("_id", None)  

            logger.info(f"User found: {user.get('uuid', 'N/A')} | Email: {user.get('email')} | Phone: {user.get('phone_number')}")
            return user

        except Exception as e:
            logger.error(f"Error in get_user_details_service: {str(e)}")
            raise e

        
    @staticmethod
    async def get_user_summary_service() -> dict:
        try:
            logger.info("Fetching user summary counts...")

            total_users = await MongoHelper.count_documents(settings.DB_TABLE.USERS, {})
            active_users = await MongoHelper.count_documents(
                settings.DB_TABLE.USERS, {"status": "ACTIVE"}
            )

            kyc_pending = await MongoHelper.count_documents(
                settings.DB_TABLE.USERS, {"kyc_status": "PENDING"}
            )

            suspended_users = await MongoHelper.count_documents(
                settings.DB_TABLE.USERS, {"status": "SUSPENDED"}
            )

            logger.info(
                f"User summary fetched successfully: "
                f"Total={total_users}, Active={active_users}, "
                f"KYC Pending={kyc_pending}, Suspended={suspended_users}"
            )

            return OutModel(
                status="success",
                status_code=200,
                comment="User summary fetched successfully",
                data={
                    "total_users": total_users,
                    "active_users": active_users,
                    "kyc_pending": kyc_pending,
                    "suspended_users": suspended_users,
                },
            )
        except Exception as e:
            logger.error(f"Error fetching user summary: {str(e)}", exc_info=True)
            return OutModel(
                status="error",
                status_code=500,
                comment="Failed to fetch user summary",
                data=None,
            )