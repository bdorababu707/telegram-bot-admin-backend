# from typing import Dict, Any
# from app.utils.logging import get_logger
# from app.utils.config import settings
# from app.db.mongo.helper import MongoHelper
# from app.models.base import OutModel

# logger = get_logger(__name__)


# class DashboardService:
#     @staticmethod
#     async def get_admin_overview() -> OutModel:
#         try:
#             # 1. Total wallet balance
#             wallet_pipeline = [
#                 {"$group": {"_id": None, "total_balance": {"$sum": "$balance"}}}
#             ]
#             wallet_result = await MongoHelper.aggregate(settings.DB_TABLE.WALLETS, wallet_pipeline)
#             total_wallet_balance = (
#                 wallet_result[0]["total_balance"] if wallet_result else 0
#             )

#             # 2. Count transactions by type
#             total_buy_grams = await MongoHelper.count_documents(
#                 settings.DB_TABLE.TRANSACTIONS,
#                 {"buy_grams": {"$gt": 0}, "sell_grams": 0, "status": "OPEN"}
#             )
#             total_sell_grams = await MongoHelper.count_documents(
#                 settings.DB_TABLE.TRANSACTIONS,
#                 {"sell_grams": {"$gt": 0}, "buy_grams": 0, "status": "OPEN"}
#             )
#             total_closed_positions = await MongoHelper.count_documents(
#                 settings.DB_TABLE.TRANSACTIONS,
#                 {"status": "CLOSED"}
#             )

#             # 3. Total users
#             total_users = await MongoHelper.count_documents(
#                 settings.DB_TABLE.USERS,
#                 {}
#             )

#             response: Dict[str, Any] = {
#                 "total_wallet_balance": total_wallet_balance,
#                 "total_buy_grams": total_buy_grams,
#                 "total_sell_grams": total_sell_grams,
#                 "total_closed_positions": total_closed_positions,
#                 "total_users": total_users,
#             }

#             return OutModel(
#                 status="success",
#                 status_code=200,
#                 comment="Admin overview fetched successfully",
#                 data=response
#             )

#         except Exception as e:
#             logger.error(f"Error fetching admin overview: {str(e)}")
#             return OutModel(
#                 status="error",
#                 status_code=500,
#                 comment="Internal server error while fetching admin overview",
#                 data=""
#             )


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
            # Wallet balance pipeline (separate)
            wallet_pipeline = [
                {"$group": {"_id": None, "total_balance": {"$sum": "$balance"}}}
            ]
            wallet_result = await MongoHelper.aggregate(settings.DB_TABLE.WALLETS, wallet_pipeline)
            total_wallet_balance = wallet_result[0]["total_balance"] if wallet_result else 0

            # Users count (separate)
            total_users = await MongoHelper.count_documents(settings.DB_TABLE.USERS, {})

            # Single pipeline for all transaction-related metrics
            transactions_pipeline = [
                {
                    "$facet": {
                        "buy_count": [
                            {"$match": {"buy_grams": {"$gt": 0}, "sell_grams": 0, "status": "OPEN"}},
                            {"$count": "count"}
                        ],
                        "sell_count": [
                            {"$match": {"sell_grams": {"$gt": 0}, "buy_grams": 0, "status": "OPEN"}},
                            {"$count": "count"}
                        ],
                        "closed_count": [
                            {"$match": {"status": "CLOSED"}},
                            {"$count": "count"}
                        ],
                        "buy_sum": [
                            {"$match": {"buy_grams": {"$gt": 0}, "sell_grams": 0, "status": "OPEN"}},
                            {"$group": {"_id": None, "total": {"$sum": "$buy_grams"}}}
                        ],
                        "sell_sum": [
                            {"$match": {"sell_grams": {"$gt": 0}, "buy_grams": 0, "status": "OPEN"}},
                            {"$group": {"_id": None, "total": {"$sum": "$sell_grams"}}}
                        ],
                        "closed_buy_sum": [
                            {"$match": {"status": "CLOSED", "buy_grams": {"$gt": 0}}},
                            {"$group": {"_id": None, "total": {"$sum": "$buy_grams"}}}
                        ],
                        "closed_sell_sum": [
                            {"$match": {"status": "CLOSED", "sell_grams": {"$gt": 0}}},
                            {"$group": {"_id": None, "total": {"$sum": "$sell_grams"}}}
                        ],
                        "total_buy_grams": [
                            {"$match": {"buy_grams": {"$gt": 0}}},
                            {"$group": {"_id": None, "total": {"$sum": "$buy_grams"}}}
                        ],
                        "total_sell_grams": [
                            {"$match": {"sell_grams": {"$gt": 0}}},
                            {"$group": {"_id": None, "total": {"$sum": "$sell_grams"}}}
                        ]
                    }
                }
            ]


            trx_result = await MongoHelper.aggregate(settings.DB_TABLE.TRANSACTIONS, transactions_pipeline)
            trx_data = trx_result[0] if trx_result else {}

            def safe_extract(data: list, key: str) -> int:
                return data[0].get(key, 0) if data and isinstance(data[0], dict) else 0

            total_buy_grams_count = safe_extract(trx_data.get("buy_count", []), "count")
            total_sell_grams_count = safe_extract(trx_data.get("sell_count", []), "count")
            total_closed_positions = safe_extract(trx_data.get("closed_count", []), "count")
            total_open_buy_grams = safe_extract(trx_data.get("buy_sum", []), "total")
            total_open_sell_grams = safe_extract(trx_data.get("sell_sum", []), "total")
            total_closed_buy_grams = safe_extract(trx_data.get("closed_buy_sum", []), "total")
            total_closed_sell_grams = safe_extract(trx_data.get("closed_sell_sum", []), "total")
            total_buy_grams = safe_extract(trx_data.get("total_buy_grams", []), "total")
            total_sell_grams = safe_extract(trx_data.get("total_sell_grams", []), "total")


            response: Dict[str, Any] = {
                "total_wallet_balance": total_wallet_balance,
                "total_buy_grams": total_buy_grams,
                "total_sell_grams": total_sell_grams,
                "total_users": total_users,
                "total_closed_positions": total_closed_positions,

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
