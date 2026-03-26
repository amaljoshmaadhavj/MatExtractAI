"""File management operations."""

import shutil
import logging
from pathlib import Path
from typing import Optional
from app.config import settings
from app.core.exceptions import FileOperationError

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file operations for uploads and results."""
    
    @staticmethod
    def save_upload(file_data: bytes, job_id: str, filename: str) -> Path:
        """
        Save uploaded PDF file.
        
        Args:
            file_data: File content as bytes
            job_id: Unique job ID
            filename: Original filename
            
        Returns:
            Path to saved file
            
        Raises:
            FileOperationError: If save fails
        """
        try:
            # Create job directory
            job_dir = settings.upload_path / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = job_dir / filename
            file_path.write_bytes(file_data)
            
            logger.info(f"Saved upload: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving upload: {e}")
            raise FileOperationError(f"Failed to save uploaded file: {e}")
    
    @staticmethod
    def save_results(data: dict, job_id: str, filename: str = "final_result.json") -> Path:
        """
        Save extraction results as JSON.
        
        Args:
            data: Results dictionary
            job_id: Unique job ID
            filename: Output filename
            
        Returns:
            Path to saved file
            
        Raises:
            FileOperationError: If save fails
        """
        try:
            import json
            
            # Create results directory
            job_dir = settings.results_path / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = job_dir / filename
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved results: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise FileOperationError(f"Failed to save results: {e}")
    
    @staticmethod
    def get_results(job_id: str, filename: str = "final_result.json") -> Optional[dict]:
        """
        Load results from JSON file.
        
        Args:
            job_id: Unique job ID
            filename: Filename to load
            
        Returns:
            Results dictionary or None if not found
        """
        try:
            import json
            
            file_path = settings.results_path / job_id / filename
            if not file_path.exists():
                logger.warning(f"Results file not found: {file_path}")
                return None
            
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading results: {e}")
            return None
    
    @staticmethod
    def delete_job_files(job_id: str, delete_uploads: bool = True, delete_results: bool = False) -> bool:
        """
        Delete job files.
        
        Args:
            job_id: Job ID
            delete_uploads: Delete upload directory
            delete_results: Delete results directory
            
        Returns:
            True if successful
        """
        try:
            if delete_uploads:
                upload_dir = settings.upload_path / job_id
                if upload_dir.exists():
                    shutil.rmtree(upload_dir)
                    logger.info(f"Deleted upload directory: {upload_dir}")
            
            if delete_results:
                results_dir = settings.results_path / job_id
                if results_dir.exists():
                    shutil.rmtree(results_dir)
                    logger.info(f"Deleted results directory: {results_dir}")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting job files: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        try:
            if file_path.exists():
                return file_path.stat().st_size
            return 0
        except Exception as e:
            logger.error(f"Error getting file size: {e}")
            return 0
