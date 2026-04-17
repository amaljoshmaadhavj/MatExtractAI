"""PDF upload endpoint."""

from fastapi import APIRouter, File, UploadFile, status, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from app.core.exceptions import PDFUploadError
from app.core.utils import validate_pdf, format_file_size, log_progress
from app.core.worker import process_pdf_job
from app.config import settings
from app.services.job_service import JobService
from app.storage.file_manager import FileManager
from app.storage.mongodb_manager import MongoDBManager
from app.models.response import JobStatusResponse
from datetime import datetime
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)
job_service = JobService()
file_manager = FileManager()
mongodb_manager = MongoDBManager()  # MongoDB Atlas (optional with fallback to file storage)


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload PDF file for processing.
    
    Args:
        file: PDF file to process
        background_tasks: FastAPI background tasks
        
    Returns:
        Job ID and status
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise PDFUploadError("File must be a PDF")
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > settings.max_file_size:
            raise PDFUploadError(
                f"File too large. Maximum size: {format_file_size(settings.max_file_size)}"
            )
        
        # Create job
        job = job_service.create_job(file.filename)
        logger.info(f"✅ [UPLOAD] Created job {job.id} for file {file.filename}")
        
        # Save job status to MongoDB
        if mongodb_manager and mongodb_manager.enabled:
            mongodb_manager.save_job_status(
                job.id,
                file.filename,
                "processing",
                progress=0,
                current_step="Uploading file"
            )
        
        # Save upload
        file_path = file_manager.save_upload(content, job.id, file.filename)
        
        # Validate PDF
        if not validate_pdf(Path(file_path)):
            error_msg = "Invalid PDF file"
            job_service.update_status(
                job.id, 
                "failed",
                error_message=error_msg
            )
            raise PDFUploadError("Invalid PDF file format")
        
        # Update job status
        job_service.update_status(
            job.id,
            "processing",
            progress=10,
            current_step="PDF received, preparing extraction"
        )
        
        # Add background task to process PDF
        if background_tasks:
            background_tasks.add_task(process_pdf_job, job.id, str(file_path))
        
        log_progress(job.id, "PDF uploaded successfully", 10)
        
        return {
            "job_id": job.id,
            "filename": file.filename,
            "status": "processing",
            "message": "File received, extraction starting..."
        }
        
    except PDFUploadError as e:
        logger.error(f"PDF upload error: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error_code": "UPLOAD_ERROR",
                "message": str(e),
                "details": "Please check the file format and size"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "UPLOAD_FAILED",
                "message": "Failed to process upload",
                "details": str(e)
            }
        )
