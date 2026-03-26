"""Job status endpoints."""

from fastapi import APIRouter, Path, status
from fastapi.responses import JSONResponse
import logging
from app.services.job_service import JobService
from app.storage.mongodb_manager import MongoDBManager
from app.config import settings
from app.core.exceptions import JobNotFoundError
from app.core.utils import get_time_estimate

router = APIRouter()
logger = logging.getLogger(__name__)
job_service = JobService()
mongodb_manager = MongoDBManager() if settings.use_mongodb else None


@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str = Path(..., description="Job ID")):
    """
    Get job status and progress.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job status information
    """
    try:
        logger.info(f"[STATUS] Retrieving job status for: {job_id}")
        
        job = job_service.get_job(job_id)
        
        if not job:
            logger.warning(f"[STATUS] Job not found in SQLite: {job_id}")
            raise JobNotFoundError(f"Job {job_id} not found")
        
        logger.info(f"[STATUS] Job found: {job_id}, status: {job.status}")
        
        # Try to get real-time progress from MongoDB
        if mongodb_manager and mongodb_manager.enabled:
            try:
                mongo_job = mongodb_manager.get_job_status(job_id)
                if mongo_job:
                    job.progress = mongo_job.get('progress', job.progress)
                    current_step = mongo_job.get('current_step', job.current_step)
                    if current_step:
                        job.current_step = current_step
                    logger.info(f"[STATUS] Updated from MongoDB: progress={job.progress}%, step={job.current_step}")
            except Exception as e:
                logger.debug(f"[STATUS] MongoDB not available: {e}")
        
        # Calculate estimated completion time
        estimated_completion = None
        if job.status == "processing" and job.progress < 100:
            estimated_completion = get_time_estimate(job.progress // 10)
        
        response = {
            "job_id": job.id,
            "filename": job.filename,
            "status": job.status,
            "progress": job.progress,
            "current_step": job.current_step,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "estimated_completion": estimated_completion,
            "error_message": job.error_message
        }
        
        logger.info(f"[STATUS] Returning status: {response}")
        return response
        
    except JobNotFoundError as e:
        logger.warning(f"[STATUS] Job not found: {job_id}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "JOB_NOT_FOUND",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"[STATUS] Error retrieving job status: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "STATUS_ERROR",
                "message": "Failed to retrieve job status",
                "details": str(e)
            }
        )


@router.get("/jobs")
async def list_jobs(limit: int = 10):
    """
    List recent jobs.
    
    Args:
        limit: Maximum number of jobs to return
        
    Returns:
        List of recent jobs
    """
    try:
        jobs = job_service.list_recent_jobs(limit)
        
        return {
            "jobs": [
                {
                    "job_id": job.id,
                    "filename": job.filename,
                    "status": job.status,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat(),
                    "updated_at": job.updated_at.isoformat()
                }
                for job in jobs
            ],
            "total": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "LIST_ERROR",
                "message": "Failed to list jobs"
            }
        )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str = Path(..., description="Job ID")):
    """
    Delete a job and its files.
    
    Args:
        job_id: Job ID
        
    Returns:
        Deletion status
    """
    try:
        success = job_service.delete_job(job_id, delete_files=True)
        
        if success:
            return {"status": "success", "message": f"Job {job_id} deleted"}
        else:
            raise JobNotFoundError(f"Job {job_id} not found")
            
    except JobNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "JOB_NOT_FOUND",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "DELETE_ERROR",
                "message": "Failed to delete job"
            }
        )
