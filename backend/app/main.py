"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.core.utils import cleanup_old_files
from app.routes import health, upload, jobs, results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting MatExtractAI backend...")
    logger.info(f"API listening on {settings.api_host}:{settings.api_port}")
    logger.info(f"CORS enabled for: {settings.frontend_url}")
    
    # Initialize MongoDB
    if settings.use_mongodb:
        try:
            from app.storage.mongodb_client import MongoDBClient
            mongo_client = MongoDBClient.get_instance()
            if mongo_client.db is not None:
                logger.info("✅ MongoDB initialized successfully")
            else:
                logger.warning("⚠️ MongoDB connection failed, using file storage fallback")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize MongoDB: {e}")
    else:
        logger.info("💾 Using local file storage (MongoDB disabled)")
    
    # Run cleanup on startup
    deleted = cleanup_old_files(settings.upload_path, settings.cleanup_days)
    logger.info(f"Cleaned up {deleted} old upload directories")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MatExtractAI backend...")


# Create FastAPI application
app = FastAPI(
    title="MatExtractAI API",
    description="API for materials data extraction from PDF research papers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="", tags=["health"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(results.router, prefix="/api/v1", tags=["results"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "MatExtractAI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
