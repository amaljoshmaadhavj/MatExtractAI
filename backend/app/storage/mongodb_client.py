"""MongoDB Atlas connection and client management."""

import logging
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """Singleton MongoDB Atlas client manager."""
    
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
        
        # Check if MongoDB is disabled in settings
        if not getattr(settings, 'mongodb_enabled', True):
            logger.info("🚫 MongoDB Atlas feature is explicitly disabled in settings")
            self._db = None
            MongoDBClient._initialized = True
            return
        
        try:
            # Check if MongoDB URL is configured
            if not settings.mongodb_url or settings.mongodb_url.strip() == "":
                logger.warning("⚠️  MongoDB Atlas URL not configured in .env")
                logger.warning("   Application will use file-based storage as fallback")
                self._db = None
                MongoDBClient._initialized = True
                return
            
            # Validate MongoDB Atlas connection string format
            if not settings.mongodb_url.startswith("mongodb+srv://"):
                logger.warning(
                    "⚠️  MongoDB connection string is not in Atlas format.\n"
                    "   Expected format: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority\n"
                    f"   Current value: {settings.mongodb_url[:50]}..."
                )
                logger.warning("   Application will use file-based storage as fallback")
                self._db = None
                MongoDBClient._initialized = True
                return
            
            # Establish MongoDB Atlas connection with TLS
            logger.info("🔗 Connecting to MongoDB Atlas...")
            self._client = MongoClient(
                settings.mongodb_url,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000,  # Reduced timeout for faster fallback
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Test connection with ping command
            self._client.admin.command('ping')
            
            # Set database reference
            self._db = self._client[settings.mongodb_database]
            
            # Create indexes for optimal performance
            self._create_indexes()
            
            logger.info(f"✅ MongoDB Atlas connected successfully")
            logger.info(f"   Database: {settings.mongodb_database}")
            logger.info(f"   Cluster: {settings.mongodb_url.split('@')[1].split('/')[0] if '@' in settings.mongodb_url else 'Unknown'}")
            
            MongoDBClient._initialized = True
            
        except ConnectionFailure as e:
            logger.warning(f"⚠️  MongoDB Atlas connection failed (Connection issue)")
            logger.warning(f"   Error: {e}")
            logger.warning(f"   Application will use file-based storage as fallback")
            logger.warning(f"   Please fix network connectivity to MongoDB Atlas")
            self._db = None
            MongoDBClient._initialized = True
        except ServerSelectionTimeoutError as e:
            logger.warning(f"⚠️  MongoDB Atlas connection timeout")
            logger.warning(f"   Error: {e}")
            logger.warning(f"   Common causes:")
            logger.warning(f"   1. Network firewall blocking MongoDB Atlas")
            logger.warning(f"   2. DNS cannot resolve [YOUR_CLUSTER].mongodb.net")
            logger.warning(f"   3. Corporate network proxy/VPN required")
            logger.warning(f"   4. Cluster IP whitelist does not include your IP")
            logger.warning(f"   Application will use file-based storage as fallback")
            self._db = None
            MongoDBClient._initialized = True
        except ValueError as e:
            logger.error(f"❌ CRITICAL: {e}")
            raise
        except Exception as e:
            logger.warning(f"⚠️  MongoDB Atlas unavailable: {type(e).__name__}")
            logger.warning(f"   Error: {e}")
            logger.warning(f"   Application will use file-based storage as fallback")
            self._db = None
            MongoDBClient._initialized = True
    
    @property
    def db(self):
        """Get database instance (may be None if unavailable)."""
        return self._db
    
    def _create_indexes(self):
        """Create necessary indexes for performance."""
        if self._db is None:
            logger.error("❌ Cannot create indexes: database not connected")
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
            
            logger.info("✅ MongoDB Atlas indexes created successfully")
        except Exception as e:
            logger.warning(f"⚠️ Warning creating indexes: {e}")
    
    def close(self):
        """Close MongoDB Atlas connection."""
        if self._client is not None:
            self._client.close()
            logger.info("✅ MongoDB Atlas connection closed")
    
    @staticmethod
    def get_instance():
        """Get MongoDB Atlas client instance."""
        return MongoDBClient()

