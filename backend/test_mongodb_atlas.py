"""Test MongoDB Atlas connection."""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.storage.mongodb_client import MongoDBClient
from app.storage.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test MongoDB Atlas connection."""
    logger.info("=" * 60)
    logger.info("Testing MongoDB Atlas Connection")
    logger.info("=" * 60)
    
    # Display settings
    logger.info(f"Database URL: {settings.mongodb_url}")
    logger.info(f"Database Name: {settings.mongodb_database}")
    logger.info(f"MongoDB Enabled: {settings.use_mongodb}")
    
    # Test connection
    try:
        client = MongoDBClient.get_instance()
        db = client.db
        
        if db is None:
            logger.error("❌ MongoDB connection failed - db is None")
            return False
        
        logger.info("✅ MongoDB Atlas connection successful")
        
        # Test collections exist
        collections = db.list_collection_names()
        logger.info(f"Available collections: {collections}")
        
        # Test ping
        db.command('ping')
        logger.info("✅ MongoDB Atlas ping successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB Atlas connection failed: {e}")
        return False


def test_save_and_retrieve():
    """Test saving and retrieving data."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Save and Retrieve Operations")
    logger.info("=" * 60)
    
    try:
        manager = MongoDBManager()
        
        if not manager.enabled:
            logger.warning("⚠️ MongoDB not enabled")
            return False
        
        # Test data
        test_job_id = "test_job_12345"
        test_results = {
            "job_id": test_job_id,
            "filename": "test_document.pdf",
            "extraction": {
                "composition": {
                    "Al": "3%",
                    "Zn": "1%"
                },
                "mechanical_properties": {
                    "yield_strength_MPa": 170
                }
            }
        }
        
        # Save
        logger.info(f"Saving test results with job_id: {test_job_id}")
        save_result = manager.save_results(test_results)
        
        if save_result:
            logger.info("✅ Results saved to MongoDB Atlas")
        else:
            logger.error("❌ Failed to save results")
            return False
        
        # Retrieve
        logger.info(f"Retrieving results for job_id: {test_job_id}")
        retrieved = manager.get_results(test_job_id)
        
        if retrieved:
            logger.info("✅ Results retrieved from MongoDB Atlas")
            logger.info(f"Retrieved data: {retrieved}")
        else:
            logger.error("❌ Failed to retrieve results")
            return False
        
        # Clean up
        logger.info(f"Deleting test job: {test_job_id}")
        delete_result = manager.delete_results(test_job_id)
        
        if delete_result:
            logger.info("✅ Test data cleaned up")
        else:
            logger.warning("⚠️ Failed to clean up test data")
        
        return True
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("\n🔍 MongoDB Atlas Configuration Test Suite\n")
    
    # Test 1: Connection
    connection_ok = test_connection()
    
    # Test 2: Save and Retrieve
    if connection_ok:
        operations_ok = test_save_and_retrieve()
    else:
        logger.error("\n❌ Skipping operations test - connection failed")
        operations_ok = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    if connection_ok and operations_ok:
        logger.info("✅ All tests passed! MongoDB Atlas is properly configured.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
