"""MongoDB data persistence layer."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo.errors import PyMongoError
from app.storage.mongodb_client import MongoDBClient
from app.config import settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Manager for MongoDB Atlas operations (Optional with fallback)."""
    
    def __init__(self):
        try:
            self.client = MongoDBClient.get_instance()
            self.db = self.client.db
            self.enabled = self.db is not None
            
            if self.enabled:
                logger.info("✅ MongoDB Manager initialized with MongoDB Atlas")
            elif getattr(settings, 'mongodb_enabled', True):
                # Only warn if MongoDB was supposed to be enabled but failed
                logger.debug("📂 Using file-based storage for job/result persistence")
            else:
                # MongoDB is explicitly disabled
                logger.debug("📂 MongoDB disabled - using file-based storage")
        except Exception as e:
            logger.warning(f"⚠️  MongoDB initialization error: {e} - using file-based fallback")
            self.db = None
            self.enabled = False
    
    def save_results(self, results: dict) -> bool:
        """
        Save extraction results to MongoDB Atlas (with fallback to file storage).
        
        Args:
            results: Results dictionary with job_id
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.debug("MongoDB not available, file storage will handle this")
            return False
        
        try:
            job_id = results.get('job_id')
            if not job_id:
                raise ValueError("Results must contain job_id")
            
            results_with_metadata = {
                'job_id': job_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'data': results,
                'status': 'completed'
            }
            
            collection = self.db['results']
            result = collection.update_one(
                {'job_id': job_id},
                {'$set': results_with_metadata},
                upsert=True
            )
            
            logger.info(f"✅ Results saved to MongoDB Atlas for job {job_id}")
            return True
        except PyMongoError as e:
            logger.warning(f"⚠️  MongoDB save failed, file storage will handle: {e}")
            return False
        except Exception as e:
            logger.warning(f"⚠️  Error saving to MongoDB: {e}, file storage will handle")
            return False
    
    def get_results(self, job_id: str) -> Optional[dict]:
        """
        Retrieve extraction results from MongoDB Atlas (with fallback).
        
        Args:
            job_id: Job ID
            
        Returns:
            Results dictionary or None
        """
        if not self.enabled:
            logger.debug("MongoDB not available, file storage will handle this")
            return None
        
        try:
            collection = self.db['results']
            document = collection.find_one({'job_id': job_id})
            
            if document:
                document.pop('_id', None)
                logger.info(f"✅ Retrieved results from MongoDB Atlas for job {job_id}")
                return document.get('data')
            
            logger.warning(f"⚠️  No results found in MongoDB Atlas for job {job_id}")
            return None
        except Exception as e:
            logger.warning(f"⚠️  Error retrieving from MongoDB: {e}, file storage will handle")
            return None
    
    def save_job_status(self, job_id: str, filename: str, status: str, 
                       progress: int = 0, current_step: str = "", 
                       error_message: Optional[str] = None) -> bool:
        """
        Save job status to MongoDB Atlas (with fallback).
        
        Args:
            job_id: Job ID
            filename: Original filename
            status: Job status
            progress: Progress percentage
            current_step: Current processing step
            error_message: Error message if failed
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.debug("MongoDB not available, file storage will handle this")
            return False
        
        try:
            job_data = {
                'job_id': job_id,
                'filename': filename,
                'status': status,
                'progress': progress,
                'current_step': current_step,
                'error_message': error_message,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            collection = self.db['jobs']
            result = collection.update_one(
                {'job_id': job_id},
                {'$set': job_data},
                upsert=True
            )
            
            logger.info(f"✅ Saved job status for {job_id} to MongoDB Atlas")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Error saving job status to MongoDB: {e}, file storage will handle")
            return False
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Retrieve job status from MongoDB Atlas (with fallback).
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dictionary or None
        """
        if not self.enabled:
            logger.debug("MongoDB not available, file storage will handle this")
            return None
        
        try:
            collection = self.db['jobs']
            document = collection.find_one({'job_id': job_id})
            
            if document:
                document.pop('_id', None)
                logger.info(f"✅ Retrieved job status from MongoDB Atlas for job {job_id}")
                return document
            
            logger.warning(f"⚠️ No job status found in MongoDB Atlas for job {job_id}")
            return None
        except Exception as e:
            logger.warning(f"⚠️  Error retrieving from MongoDB: {e}, file storage will handle")
            return None
    
    def update_job_progress(self, job_id: str, progress: int, 
                           current_step: str = "") -> bool:
        """
        Update job progress in real-time on MongoDB Atlas (with fallback).
        
        Args:
            job_id: Job ID
            progress: Progress percentage (0-100)
            current_step: Current processing step
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.debug("MongoDB not available, file storage will handle this")
            return False
        
        try:
            collection = self.db['jobs']
            collection.update_one(
                {'job_id': job_id},
                {
                    '$set': {
                        'progress': progress,
                        'current_step': current_step,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            logger.debug(f"✅ Job progress updated: {job_id} - {progress}% - {current_step}")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Error updating job progress: {e}, file storage will handle")
            return False
    
    def delete_results(self, job_id: str) -> bool:
        """
        Delete results from MongoDB Atlas (with fallback).
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.debug("MongoDB not available, file storage will handle this")
            return False
        
        try:
            self.db['results'].delete_one({'job_id': job_id})
            self.db['jobs'].delete_one({'job_id': job_id})
            logger.info(f"✅ Deleted job {job_id} from MongoDB Atlas")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Error deleting job: {e}, file storage will handle")
            return False
    
    def list_jobs(self, status: Optional[str] = None, 
                 limit: int = 100) -> List[dict]:
        """
        List jobs from MongoDB Atlas (with fallback).
        
        Args:
            status: Filter by status (optional)
            limit: Maximum number of results
            
        Returns:
            List of job documents or empty list
        """
        if not self.enabled:
            logger.debug("MongoDB not available, file storage will handle this")
            return []
        
        try:
            collection = self.db['jobs']
            query = {}
            if status:
                query['status'] = status
            
            jobs = list(collection.find(query).limit(limit).sort('created_at', -1))
            for job in jobs:
                job.pop('_id', None)
            
            logger.info(f"✅ Retrieved {len(jobs)} jobs from MongoDB Atlas")
            return jobs
        except Exception as e:
            logger.warning(f"⚠️  Error listing jobs: {e}, file storage will handle")
            return []
