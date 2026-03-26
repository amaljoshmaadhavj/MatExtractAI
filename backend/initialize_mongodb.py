#!/usr/bin/env python
"""Initialize MongoDB with collections and indexes."""

import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.storage.mongodb_client import MongoDBClient
from app.storage.mongodb_manager import MongoDBManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_mongodb():
    """Initialize MongoDB with collections and sample data."""
    
    logger.info("=" * 60)
    logger.info("MongoDB Initialization Script")
    logger.info("=" * 60)
    
    # Get MongoDB client
    logger.info(f"MongoDB URL: {settings.mongodb_url}")
    logger.info(f"Database: {settings.mongodb_database}")
    
    client = MongoDBClient.get_instance()
    
    if client.db is None:
        logger.error("❌ Failed to connect to MongoDB")
        return False
    
    logger.info("✅ Connected to MongoDB successfully!")
    
    db = client.db
    
    # Create collections
    logger.info("\nCreating collections...")
    
    try:
        # Results collection
        if 'results' not in db.list_collection_names():
            db.create_collection('results')
            logger.info("✅ Created 'results' collection")
        else:
            logger.info("ℹ️  'results' collection already exists")
        
        # Jobs collection
        if 'jobs' not in db.list_collection_names():
            db.create_collection('jobs')
            logger.info("✅ Created 'jobs' collection")
        else:
            logger.info("ℹ️  'jobs' collection already exists")
        
        # Create indexes
        logger.info("\nCreating indexes...")
        
        results_col = db['results']
        results_col.create_index('job_id', unique=True)
        results_col.create_index('created_at')
        results_col.create_index('updated_at')
        logger.info("✅ Created indexes on 'results' collection")
        
        jobs_col = db['jobs']
        jobs_col.create_index('job_id', unique=True)
        jobs_col.create_index('status')
        jobs_col.create_index('created_at')
        logger.info("✅ Created indexes on 'jobs' collection")
        
        # Insert sample data
        logger.info("\nInserting sample data...")
        
        sample_result = {
            'job_id': 'sample-001',
            'filename': 'sample.pdf',
            'status': 'completed',
            'sections': {
                'abstract': 'Sample abstract text',
                'introduction': 'Sample introduction',
                'methods': 'Sample methods'
            },
            'mechanical_properties': {
                'extracted_data': [
                    {
                        'property': 'Tensile Strength',
                        'value': 250,
                        'unit': 'MPa',
                        'confidence': 0.95
                    }
                ]
            }
        }
        
        try:
            results_col.insert_one(sample_result)
            logger.info("✅ Inserted sample results document")
        except Exception as e:
            logger.info(f"ℹ️  Sample data already exists or insert skipped: {e}")
        
        # Verify data
        logger.info("\nVerifying data...")
        
        results_count = results_col.count_documents({})
        jobs_count = jobs_col.count_documents({})
        
        logger.info(f"📊 Results collection: {results_count} document(s)")
        logger.info(f"📊 Jobs collection: {jobs_count} document(s)")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ MongoDB initialization completed successfully!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    success = initialize_mongodb()
    sys.exit(0 if success else 1)
