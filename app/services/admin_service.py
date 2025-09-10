import time
from app.db.mongo.helper import MongoHelper
from app.utils.common import generate_uuid
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.logging import get_logger
from app.utils.config import settings
from app.models.admin import SuperAdmin, Admin
from app.schemas.admin import CreateSuperAdmin, CreateAdmin
from app.models.base import OutModel

logger = get_logger(__name__)

class AdminService:
    @staticmethod
    async def create_super_admin(payload:CreateSuperAdmin, secret_key: str) -> OutModel:
        """
        Create a super admin after validating secret key and duplicates.
        """
        # Verify secret key
        if secret_key != settings.SECRET_KEYS.SUPER_ADMIN_SECRET_KEY:
            logger.warning("Invalid secret key for Super Admin creation")
            return OutModel(
                status="failure",
                status_code=403,
                comment="Invalid secret key",
                data=None,
            )

        # Check duplicate email
        existing_email = await MongoHelper.find_one(
            settings.DB_TABLE.ADMINS, {"email": payload.email}
        )
        if existing_email:
            logger.warning(f"Duplicate super admin email: {payload.email}")
            return OutModel(
                status="failure",
                status_code=400,
                comment="Email already exists",
                data=None,
            )

        # Check duplicate phone
        existing_phone = await MongoHelper.find_one(
            settings.DB_TABLE.ADMINS, {"phone_number": payload.phone_number}
        )
        if existing_phone:
            logger.warning(f"Duplicate super admin phone: {payload.phone_number}")
            return OutModel(
                status="failure",
                status_code=400,
                comment="Phone number already exists",
                data=None,
            )

        now = int(time.time())
        # Prepare admin data
        admin_data = SuperAdmin(
            uuid=await generate_uuid(),
            firstname=payload.firstname,
            surname=payload.surname,
            email=payload.email,
            country=payload.country,
            country_code=payload.country_code,
            phone_number=payload.phone_number,
            password=await hash_password(payload.password),
            user_type="SUPER_ADMIN",
            created_at=now,
            updated_at=now,
        ).model_dump()

        try:
            # Insert into DB
            logger.info(f"Creating super admin: {payload.email}")
            await MongoHelper.insert_one(settings.DB_TABLE.ADMINS, admin_data)
            logger.info(f"Super admin created: {payload.email}")

            admin_data.pop("_id", None)
            admin_data.pop("password", None)
            return OutModel(
                status="success",
                status_code=201,
                comment="Super admin created successfully",
                data=admin_data,
            )
        except Exception as e:
            logger.error(f"Error creating super admin: {payload.email}: {str(e)}")
            return OutModel(
                status="error",
                status_code=500,
                comment="Failed to create super admin",
                data=str(e),
            )
        
    @staticmethod
    async def create_admin_service(current_admin: dict, payload: CreateAdmin) -> dict:
        try:
            # Check permission
            if current_admin.get("user_type") != "DEPT_ADMIN":
                return OutModel(
                    status="failure",
                    status_code=403,
                    comment="Access Denied. You dont have permission to create Admins",
                    data=None
                )

            # Check email duplication
            existing_email = await MongoHelper.find_one(
                settings.DB_TABLE.ADMINS, {"email": payload.email}
            )
            if existing_email:
                return OutModel(
                    status="failure",
                    status_code=400,
                    comment="Email already exists",
                    data=None
                )

            # Check phone duplication
            existing_phone = await MongoHelper.find_one(
                settings.DB_TABLE.ADMINS, {"phone_number": payload.phone_number}
            )

            if existing_phone:
                return OutModel(
                    status="failure",
                    status_code=400,
                    comment="Phone number already exists",
                    data=None
                )
            
            now = int(time.time())
            # Create admin document
            new_admin = Admin(
                uuid=await generate_uuid(),
                firstname=payload.firstname,
                surname=payload.surname,
                email=payload.email,
                country=payload.country,
                country_code=payload.country_code,
                phone_number=payload.phone_number,
                password=await hash_password(payload.password),
                user_type="ADMIN",
                user_roles=payload.user_roles,
                company_id=current_admin["company_id"],
                created_by=current_admin["uuid"],
                created_at=now,
                updated_at=now,
            ).model_dump()

            await MongoHelper.insert_one(
                settings.DB_TABLE.ADMINS, new_admin
            )

            logger.info(f"Admin created by {current_admin['uuid']}: {new_admin['uuid']}")

            new_admin.pop("_id", None)
            new_admin.pop("password", None)
            return OutModel(
                status="success",
                status_code=201,
                comment="Admin created successfully",
                data=new_admin
            )

        except Exception as e:
            logger.error(f"Failed to create admin: {str(e)}")
            return OutModel(
                status="error",
                status_code=500,
                comment=f"Failed to create admin: {str(e)}",
                data=None,
            )
        
    @staticmethod
    async def get_current_user_details(current_user: dict) -> dict:
        try:
            # Fetch from DB to get latest details
            user = await MongoHelper.find_one(
                settings.DB_TABLE.ADMINS,
                {"uuid": current_user["uuid"]}
            )

            if not user:
                logger.info(f"User not found: {current_user['uuid']}")
                return OutModel(
                    status="failure",
                    status_code=404,
                    comment="User not found",
                    data=None
                )

            feilds_to_remove = ["_id", "created_at", "updated_at", "password"]
            for field in feilds_to_remove:
                user.pop(field, None) 
            
            logger.info(f"Successfully Fetched current user details: {user}")
            return OutModel(
                status="success",
                status_code=200,
                comment="Current user details fetched successfully",
                data=user
            )
        except Exception as e:
            logger.error(f"Failed to fetch current user details: {str(e)}")
            return OutModel(
                status="error",
                status_code=500,
                comment=f"Failed to fetch current user details: {str(e)}",
                data=None
            )
        
    @staticmethod
    async def admin_login(email: str, password: str) -> OutModel:
        try:
            # Find admin by email
            admin = await MongoHelper.find_one(
                settings.DB_TABLE.ADMINS,
                {"email": email}
            )

            if not admin:
                logger.info(f"Admin not found for email: {email}")
                return OutModel(
                    status="error",
                    status_code=404,
                    comment="Invalid email or password",
                    data=None
                )

            # Verify password
            if not await verify_password(password, admin["password"]):
                logger.info(f"Invalid credentials for email: {email}")
                return OutModel(
                    status="error",
                    status_code=401,
                    comment="Invalid email or password",
                    data=None
                )

            # Generate JWT
            token_data = {
                "uuid": admin["uuid"],
                "email": admin["email"]
            }

            logger.info(f"Creating JWT for admin: {admin['uuid']} with email: {admin['email']}")

            access_token = await create_access_token(data=token_data)

            logger.info(f"JWT created with email: {admin['email']} : {access_token}")
            return OutModel(
                status="success",
                status_code=200,
                comment="Login successful",
                data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    # "admin_id": admin["uuid"],
                    # "email": admin["email"],
                    # "user_type": admin.get("user_type")
                }
            )

        except Exception as e:
            logger.error(f"Failed to login admin: {str(e)}")
            return OutModel(
                status="error",
                status_code=500,
                comment=f"Failed to login admin: {str(e)}",
                data=None
            )