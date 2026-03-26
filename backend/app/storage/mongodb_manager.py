"""MongoDB data persistence layer."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo.errors import PyMongoError
from app.storage.mongodb_client import MongoDBClient
from app.config import settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Manager for MongoDB operations."""
    
    def __init__(self):
        self.client = MongoDBClient.get_instance()
        self.db = self.client.db
        self.enabled = self.db is not None and settings.use_mongodb
    
    def save_results(self, results: dict) -> bool:
        """
        Save extraction results to MongoDB Atlas.
        
        Args:
            results: Results dictionary with job_id
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.debug("MongoDB not enabled, skipping results save")
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
            logger.error(f"❌ MongoDB Atlas error saving results: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error saving results to MongoDB Atlas: {e}")
            return False
    
    def get_results(self, job_id: str) -> Optional[dict]:
        """
        Retrieve extraction results from MongoDB Atlas.
        
        Args:
            job_id: Job ID
            
        Returns:
            Results dictionary or None
        """
        if not self.enabled:
            logger.debug("MongoDB not enabled")
            return None
        
        try:
            collection = self.db['results']
            document = collection.find_one({'job_id': job_id})
            
            if document:
                # Remove MongoDB internal _id field
                document.pop('_id', None)
                logger.info(f"✅ Retrieved results from MongoDB Atlas for job {job_id}")
                return document.get('data')
            
            logger.warning(f"⚠️ No results found in MongoDB Atlas for job {job_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Error retrieving results from MongoDB Atlas: {e}")
            return None
    
    def save_job_status(self, job_id: str, filename: str, status: str, 
                       progress: int = 0, current_step: str = "", 
                       error_message: Optional[str] = None) -> bool:
        """
        Save job status to MongoDB.
        
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
            logger.debug("MongoDB not enabled, skipping job status save")
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
            
            logger.info(f"Saved job status for {job_id} to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Error saving job status to MongoDB: {e}")
            return False
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Retrieve job status from MongoDB.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dictionary or None
        """
        if not self.enabled:
            return None
        
        try:
            collection = self.db['jobs']
            document = collection.find_one({'job_id': job_id})
            
            if document:
                document.pop('_id', None)
                return document
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving job status from MongoDB: {e}")
            return None
    
    def update_job_progress(self, job_id: str, progress: int, 
                           current_step: str = "") -> bool:
        """
        Update job progress in real-time.
        
        Args:
            job_id: Job ID
            progress: Progress percentage (0-100)
            current_step: Current processing step
            
        Returns:
            True if successful
        """
        if not self.enabled:
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
            return True
        except Exception as e:
            logger.error(f"Error updating job progress: {e}")
            return False
    
    def delete_results(self, job_id: str) -> bool:
        """
        Delete results from MongoDB.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            self.db['results'].delete_one({'job_id': job_id})
            self.db['jobs'].delete_one({'job_id': job_id})
            logger.info(f"Deleted job {job_id} from MongoDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting job from MongoDB: {e}")
            return False
    
    def list_jobs(self, status: Optional[str] = None, 
                 limit: int = 100) -> List[dict]:
        """
        List jobs from MongoDB.
        
        Args:
            status: Filter by status (optional)
            limit: Maximum number of results
            
        Returns:
            List of job documents
        """
        if not self.enabled:
            return []
        
        try:
            collection = self.db['jobs']
            query = {}
            if status:
                query['status'] = status
            
            jobs = list(collection.find(query).limit(limit).sort('created_at', -1))
            for job in jobs:
                job.pop('_id', None)
            
            return jobs
        except Exception as e:
            logger.error(f"Error listing jobs from MongoDB: {e}")
            return []
