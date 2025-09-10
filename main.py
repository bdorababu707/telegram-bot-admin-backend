# --- app/main.py ---

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from app.utils.logging import setup_logging, get_logger
from app.utils.security import create_access_token,verify_password
from app.db.mongo.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
    initialize_collections,
    get_database,
)
from app.db.mongo.helper import MongoHelper
from app.utils.logging import get_logger
from app.utils.config import settings
from app.api.v1 import router as v1_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


# Define application lifespan for handling startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Handles all startup and shutdown events.
    """
    # ----- STARTUP SECTION -----
    logger.info("Application starting up...")

    # Connect to MongoDB and initialize collections
    try:
        await connect_to_mongodb()
        await initialize_collections()
    except Exception as e:
        logger.critical(f"Admin App: MongoDB connection failed - {str(e)}")
        # Let the exception propagate to prevent app startup if DB connection fails
        raise

    # Add any other startup tasks here:
    # - Initialize Redis
    # - Setup background tasks
    # - Load application cache
    # - Initialize external services
    # etc.

    logger.info("Admin App: Application Startup completed successfully")

    # ----- RUNTIME SECTION -----
    yield  # This is where the application runs

    # ----- SHUTDOWN SECTION -----
    logger.info("Application shutting down...")
    
    #close mongodb connection 
    try:
        await close_mongodb_connection()
    except Exception as e:
        logger.error(f"Admin App: MongoDB disconnect error - {str(e)}")

    # Add any other cleanup tasks here:
    # - Close Redis connections
    # - Cancel background tasks
    # - Notify external services
    # etc.
    logger.info("Admin App: Shutdown completed successfully")


# Create FastAPI application
app = FastAPI(
    title=settings.APP.TITLE,
    description=settings.APP.DESCRIPTION,
    version=settings.APP.VERSION,
    docs_url=settings.APP.DOCS_URL,
    redoc_url=settings.APP.REDOC_URL,
    openapi_url=settings.APP.OPENAPI_URL,
    lifespan=lifespan  # This handles all startup/shutdown processes
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Admin health check endpoint
@app.get("/health")
async def health_check():
    """Check if the application is running and connected to MongoDB"""
    try:
        # Get database instance
        db = get_database()
        
        # Ping MongoDB to check connection
        is_connected = await db.command("ping")
        
        if is_connected:
            return {
                "status": "healthy",
                "database": "connected",
                "mode": "development" if settings.is_development() else "production",
                "version": settings.APP.VERSION
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

# Admin routes
app.include_router(v1_router, prefix="/v1")

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        email = form_data.username 
        password = form_data.password

        admin = await MongoHelper.find_one(settings.DB_TABLE.ADMINS, {"email": email})
        if not admin or not await verify_password(password, admin["password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = await create_access_token(data={"admin_id": admin["uuid"]})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        logger.error(f"Token login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )


# Uvicorn execution
if __name__ == "__main__":
    import uvicorn

    # Start the FastAPI application with Uvicorn
    logger.info(f"Starting application in {'development' if settings.is_development() else 'production'} mode")

    # Run the application using Uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER.HOST,
        port=settings.SERVER.PORT,
        reload=settings.SERVER.RELOAD
    )