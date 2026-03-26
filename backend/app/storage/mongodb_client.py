"""MongoDB connection and client management."""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """Singleton MongoDB client manager."""
    
    _instance = None
    _client = None
    _db = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        try:
            # Check if using local MongoDB or Atlas
            is_local = settings.mongodb_url.startswith("mongodb://localhost") or settings.mongodb_url == "mongodb://localhost:27017"
            
            if is_local:
                # Use mongomock for local development
                try:
                    import mongomock
                    logger.info("Using mongomock for local MongoDB emulation")
                    self._client = mongomock.MongoClient(settings.mongodb_url)
                except ImportError:
                    logger.warning("mongomock not installed. Install with: pip install mongomock")
                    self._db = None
                    MongoDBClient._initialized = True
                    return
            else:
                # Use MongoDB Atlas with TLS
                import certifi
                self._client = MongoClient(
                    settings.mongodb_url,
                    tls=True,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=10000,
                    connectTimeoutMS=15000,
                    socketTimeoutMS=15000,
                    retryWrites=True,
                    maxPoolSize=50,
                    minPoolSize=10
                )
            
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[settings.mongodb_database]
            self._create_indexes()
            connection_type = "mongomock" if is_local else "MongoDB Atlas"
            logger.info(f"✅ {connection_type} connected successfully to database: {settings.mongodb_database}")
            MongoDBClient._initialized = True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"⚠️ MongoDB connection warning: {e}. Will operate in degraded mode.")
            self._db = None
            MongoDBClient._initialized = True
        except Exception as e:
            logger.warning(f"⚠️ MongoDB initialization error: {e}")
            self._db = None
            MongoDBClient._initialized = True
    
    @property
    def db(self):
        """Get database instance."""
        return self._db
    
    def _create_indexes(self):
        """Create necessary indexes for performance."""
        if self._db is None:
            return
        
        try:
            # Results collection indexes
            results_collection = self._db['results']
            results_collection.create_index('job_id', unique=True)
            results_collection.create_index('created_at')
            results_collection.create_index('updated_at')
            
            # Jobs collection indexes
            jobs_collection = self._db['jobs']
            jobs_collection.create_index('job_id', unique=True)
            jobs_collection.create_index('status')
            jobs_collection.create_index('created_at')
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def close(self):
        """Close MongoDB connection."""
        if self._client is not None:
            self._client.close()
            logger.info("MongoDB connection closed")
    
    @staticmethod
    def get_instance():
        """Get MongoDB client instance."""
        return MongoDBClient()
