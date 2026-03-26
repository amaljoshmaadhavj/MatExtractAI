"""Job state management using SQLite."""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.config import settings
from app.models.response import JobModel

logger = logging.getLogger(__name__)


class JobStateManager:
    """Manages job metadata and state using SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize job state manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or settings.results_path / "jobs.db"
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        try:
            logger.info(f"[SQLITE] Initializing database at: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'processing',
                    progress INTEGER NOT NULL DEFAULT 0,
                    current_step TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"✅ [SQLITE] Database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"❌ [SQLITE] Error initializing database: {e}")
            raise
    
    def create_job(self, job_id: str, filename: str) -> JobModel:
        """
        Create a new job record.
        
        Args:
            job_id: Unique job ID
            filename: Original filename
            
        Returns:
            JobModel instance
        """
        now = datetime.utcnow().isoformat()
        
        try:
            logger.info(f"[SQLITE] Creating job: {job_id}, filename: {filename}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO jobs (id, filename, status, progress, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (job_id, filename, "processing", 0, now, now))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ [SQLITE] Job created successfully: {job_id}")
            return self.get_job(job_id)
        except Exception as e:
            logger.error(f"❌ [SQLITE] Error creating job {job_id}: {e}", exc_info=True)
            raise
    
    def get_job(self, job_id: str) -> Optional[JobModel]:
        """
        Retrieve job record.
        
        Args:
            job_id: Job ID to retrieve
            
        Returns:
            JobModel instance or None
        """
        try:
            logger.info(f"[SQLITE] Retrieving job: {job_id}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.warning(f"[SQLITE] Job not found: {job_id}")
                return None
            
            logger.info(f"✅ [SQLITE] Job found: {job_id}")
            # Column order: id(0), filename(1), status(2), progress(3), current_step(4), created_at(5), updated_at(6), error_message(7)
            return JobModel(
                id=row[0],
                filename=row[1],
                status=row[2],
                progress=row[3],
                current_step=row[4] or "",
                created_at=datetime.fromisoformat(row[5]),
                updated_at=datetime.fromisoformat(row[6]),
                error_message=row[7]
            )
        except Exception as e:
            logger.error(f"❌ [SQLITE] Error retrieving job {job_id}: {e}", exc_info=True)
            return None
    
    def update_job_status(self, job_id: str, status: str, progress: int = None, 
                         current_step: str = None, error_message: str = None) -> bool:
        """
        Update job status and progress.
        
        Args:
            job_id: Job ID to update
            status: New status
            progress: Progress percentage
            current_step: Current processing step
            error_message: Error message if any
            
        Returns:
            True if successful, False otherwise
        """
        now = datetime.utcnow().isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if progress is not None and current_step is not None:
                cursor.execute("""
                    UPDATE jobs 
                    SET status = ?, progress = ?, current_step = ?, updated_at = ?, error_message = ?
                    WHERE id = ?
                """, (status, progress, current_step, now, error_message, job_id))
            else:
                cursor.execute("""
                    UPDATE jobs 
                    SET status = ?, updated_at = ?, error_message = ?
                    WHERE id = ?
                """, (status, now, error_message, job_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated job {job_id}: status={status}, progress={progress}")
            return True
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            return False
    
    def list_jobs(self, limit: int = 10) -> List[JobModel]:
        """
        List recent jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobModel instances
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM jobs 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            jobs = []
            for row in rows:
                # Column order: id(0), filename(1), status(2), progress(3), current_step(4), created_at(5), updated_at(6), error_message(7)
                jobs.append(JobModel(
                    id=row[0],
                    filename=row[1],
                    status=row[2],
                    progress=row[3],
                    current_step=row[4] or "",
                    created_at=datetime.fromisoformat(row[5]),
                    updated_at=datetime.fromisoformat(row[6]),
                    error_message=row[7]
                ))
            
            return jobs
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            return []
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete job record.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            return False