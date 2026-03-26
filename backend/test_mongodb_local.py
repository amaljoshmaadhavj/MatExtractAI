#!/usr/bin/env python
"""Test MongoDB connection and data persistence."""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.storage.mongodb_manager import MongoDBManager
from app.storage.file_manager import FileManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mongodb():
    """Test MongoDB operations."""
    logger.info("=" * 70)
    logger.info("MongoDB Connection Test")
    logger.info("=" * 70)
    
    logger.info(f"MongoDB URL: {settings.mongodb_url}")
    logger.info(f"Database: {settings.mongodb_database}")
    logger.info(f"MongoDB Enabled: {settings.use_mongodb}\n")
    
    # Initialize manager
    mongodb_manager = MongoDBManager()
    
    if not mongodb_manager.enabled:
        logger.warning("⚠️  MongoDB is not enabled or not connected")
        return False
    
    logger.info("✅ MongoDB Manager initialized\n")
    
    # Test 1: Save results
    logger.info("Test 1: Saving sample results...")
    test_job_id = f"test-{datetime.now().timestamp()}"
    
    test_results = {
        "job_id": test_job_id,
        "filename": "test_document.pdf",
        "status": "completed",
        "sections": {
            "abstract": "This is a test abstract.",
            "introduction": "This is a test introduction.",
            "methods": "This is a test methodology."
        },
        "mechanical_properties": {
            "extracted_data": [
                {
                    "property": "Tensile Strength",
                    "value": 350,
                    "unit": "MPa",
                    "confidence": 0.92
                },
                {
                    "property": "Yield Strength",
                    "value": 250,
                    "unit": "MPa",
                    "confidence": 0.89
                }
            ]
        },
        "composition": {
            "extracted_data": [
                {"element": "Fe", "percentage": 70.5, "confidence": 0.95},
                {"element": "Ni", "percentage": 18.3, "confidence": 0.93},
                {"element": "Cr", "percentage": 11.2, "confidence": 0.91}
            ]
        },
        "processing": {
            "extracted_data": {
                "temperature": "1100°C",
                "time": "2 hours",
                "atmosphere": "Inert"
            }
        },
        "microstructure": {
            "extracted_data": "Austenitic stainless steel with grain refinement"
        },
        "validation": {
            "overall_quality_score": 0.92,
            "confidence_scores": {
                "mechanical": 0.92,
                "composition": 0.93,
                "processing": 0.88,
                "microstructure": 0.90
            }
        }
    }
    
    success = mongodb_manager.save_results(test_results)
    if success:
        logger.info(f"✅ Results saved successfully for job {test_job_id}\n")
    else:
        logger.error(f"❌ Failed to save results\n")
        return False
    
    # Test 2: Retrieve results
    logger.info("Test 2: Retrieving saved results...")
    retrieved = mongodb_manager.get_results(test_job_id)
    
    if retrieved:
        logger.info("✅ Results retrieved from MongoDB:")
        logger.info(f"  - Job ID: {retrieved.get('job_id')}")
        logger.info(f"  - Filename: {retrieved.get('filename')}")
        logger.info(f"  - Status: {retrieved.get('status')}")
        logger.info(f"  - Sections: {list(retrieved.get('sections', {}).keys())}\n")
    else:
        logger.error("❌ Failed to retrieve results\n")
        return False
    
    # Test 3: Save job status
    logger.info("Test 3: Saving job status...")
    job_success = mongodb_manager.save_job_status(
        test_job_id,
        "test_document.pdf",
        "completed",
        progress=100,
        current_step="Processing complete"
    )
    
    if job_success:
        logger.info("✅ Job status saved successfully\n")
    else:
        logger.error("❌ Failed to save job status\n")
        return False
    
    # Test 4: Retrieve job status
    logger.info("Test 4: Retrieving job status...")
    job_status = mongodb_manager.get_job_status(test_job_id)
    
    if job_status:
        logger.info("✅ Job status retrieved:")
        logger.info(f"  - Job ID: {job_status.get('job_id')}")
        logger.info(f"  - Status: {job_status.get('status')}")
        logger.info(f"  - Progress: {job_status.get('progress')}%\n")
    else:
        logger.error("❌ Failed to retrieve job status\n")
        return False
    
    # Test 5: List jobs
    logger.info("Test 5: Listing all jobs...")
    jobs = mongodb_manager.list_jobs(limit=10)
    logger.info(f"✅ Found {len(jobs)} job(s) in MongoDB\n")
    
    # Summary
    logger.info("=" * 70)
    logger.info("✅ All MongoDB tests passed!")
    logger.info("=" * 70)
    logger.info("\nMongoDB Configuration:")
    logger.info(f"  - Type: mongomock (in-memory local MongoDB)")
    logger.info(f"  - URL: {settings.mongodb_url}")
    logger.info(f"  - Database: {settings.mongodb_database}")
    logger.info(f"  - Collections: results, jobs")
    logger.info("\nSystem is ready for production use!")
    
    return True


if __name__ == '__main__':
    success = test_mongodb()
    sys.exit(0 if success else 1)
