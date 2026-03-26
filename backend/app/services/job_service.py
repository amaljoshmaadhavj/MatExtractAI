"""Job service for job management."""

import logging
from datetime import datetime
from typing import Optional
from app.storage.job_state import JobStateManager
from app.storage.file_manager import FileManager
from app.models.response import JobModel
from app.core.utils import generate_job_id

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing job lifecycle."""
    
    def __init__(self):
        """Initialize job service."""
        self.state_manager = JobStateManager()
        self.file_manager = FileManager()
    
    def create_job(self, filename: str) -> JobModel:
        """
        Create a new job.
        
        Args:
            filename: Original filename
            
        Returns:
            Created JobModel
        """
        job_id = generate_job_id()
        job = self.state_manager.create_job(job_id, filename)
        logger.info(f"Created job: {job_id}")
        return job
    
    def get_job(self, job_id: str) -> Optional[JobModel]:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            JobModel or None if not found
        """
        return self.state_manager.get_job(job_id)
    
    def update_status(self, job_id: str, status: str, progress: int = None,
                     current_step: str = None, error_message: str = None) -> bool:
        """
        Update job status.
        
        Args:
            job_id: Job ID
            status: New status
            progress: Progress percentage
            current_step: Current processing step
            error_message: Error message if any
            
        Returns:
            True if successful
        """
        return self.state_manager.update_job_status(
            job_id, status, progress, current_step, error_message
        )
    
    def list_recent_jobs(self, limit: int = 10) -> list:
        """
        List recent jobs.
        
        Args:
            limit: Maximum jobs to return
            
        Returns:
            List of JobModels
        """
        return self.state_manager.list_jobs(limit)
    
    def delete_job(self, job_id: str, delete_files: bool = True) -> bool:
        """
        Delete job and optionally its files.
        
        Args:
            job_id: Job ID
            delete_files: Whether to delete associated files
            
        Returns:
            True if successful
        """
        if delete_files:
            self.file_manager.delete_job_files(job_id, delete_uploads=True, delete_results=True)
        
        return self.state_manager.delete_job(job_id)
