from typing import Dict, Any
from app.utils.logging import get_logger
from app.utils.config import settings
from app.db.mongo.helper import MongoHelper
from app.models.base import OutModel

logger = get_logger(__name__)


class DashboardService:
    @staticmethod
    async def get_admin_overview() -> OutModel:
        try:
            # 1. Total wallet balance
            wallet_pipeline = [
                {"$group": {"_id": None, "total_balance": {"$sum": "$balance"}}}
            ]
            wallet_result = await MongoHelper.aggregate(settings.DB_TABLE.WALLETS, wallet_pipeline)
            total_wallet_balance = (
                wallet_result[0]["total_balance"] if wallet_result else 0
            )

            # 2. Count transactions by type
            total_buy_positions = await MongoHelper.count_documents(
                settings.DB_TABLE.TRANSACTIONS,
                {"buy_grams": {"$gt": 0}, "sell_grams": 0, "status": "OPEN"}
            )
            total_sell_positions = await MongoHelper.count_documents(
                settings.DB_TABLE.TRANSACTIONS,
                {"sell_grams": {"$gt": 0}, "buy_grams": 0, "status": "OPEN"}
            )
            total_closed_positions = await MongoHelper.count_documents(
                settings.DB_TABLE.TRANSACTIONS,
                {"status": "CLOSED"}
            )

            # 3. Total users
            total_users = await MongoHelper.count_documents(
                settings.DB_TABLE.USERS,
                {}
            )

            response: Dict[str, Any] = {
                "total_wallet_balance": total_wallet_balance,
                "total_buy_positions": total_buy_positions,
                "total_sell_positions": total_sell_positions,
                "total_closed_positions": total_closed_positions,
                "total_users": total_users,
            }

            return OutModel(
                status="success",
                status_code=200,
                comment="Admin overview fetched successfully",
                data=response
            )

        except Exception as e:
            logger.error(f"Error fetching admin overview: {str(e)}")
            return OutModel(
                status="error",
                status_code=500,
                comment="Internal server error while fetching admin overview",
                data=""
            )
