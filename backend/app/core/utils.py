"""Utility functions for the application."""

import uuid
import shutil
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def generate_job_id() -> str:
    """Generate a unique job ID using UUID."""
    return str(uuid.uuid4())


def validate_pdf(file_path: Path) -> bool:
    """
    Validate if file is a PDF by checking magic bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is valid PDF, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            magic = f.read(4)
            return magic == b'%PDF'
    except Exception as e:
        logger.error(f"Error validating PDF: {e}")
        return False


def cleanup_old_files(dir_path: Path, days: int = 7) -> int:
    """
    Delete files older than specified number of days.
    
    Args:
        dir_path: Directory to clean
        days: Age threshold in days
        
    Returns:
        Number of files deleted
    """
    if not dir_path.exists():
        return 0
    
    deleted_count = 0
    cutoff_time = time.time() - (days * 86400)
    
    try:
        for job_dir in dir_path.iterdir():
            if job_dir.is_dir() and job_dir.stat().st_mtime < cutoff_time:
                shutil.rmtree(job_dir)
                deleted_count += 1
                logger.info(f"Cleaned up old job directory: {job_dir.name}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    
    return deleted_count


def format_file_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable size string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_time_estimate(processing_step: int, total_steps: int = 10) -> int:
    """
    Estimate time remaining based on current step.
    
    Args:
        processing_step: Current processing step (0-10)
        total_steps: Total steps in process
        
    Returns:
        Estimated seconds remaining
    """
    avg_time_per_step = 30  # Average 30 seconds per step
    remaining_steps = max(0, total_steps - processing_step)
    return remaining_steps * avg_time_per_step


def log_progress(job_id: str, message: str, progress: int = 0) -> None:
    """
    Log progress for a job.
    
    Args:
        job_id: Job ID
        message: Progress message
        progress: Progress percentage (0-100)
    """
    logger.info(f"[Job {job_id}] ({progress}%) {message}")
