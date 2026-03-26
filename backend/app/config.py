import os
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    debug: bool = Field(default=False, json_schema_extra={'allow_mutation': True})
    
    # File storage
    upload_dir: str = "./uploads"
    results_dir: str = "./results"
    logs_dir: str = "./logs"
    max_file_size: int = 52428800  # 50MB
    
    # Processing
    job_timeout: int = 1800  # 30 minutes
    cleanup_days: int = 7
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    
    # Logging
    log_level: str = "INFO"
    
    # MongoDB - Local for development, change to MongoDB Atlas if needed
    # Local: mongodb_url: str = "mongodb://localhost:27017"
    # Atlas: mongodb_url: str = "mongodb+srv://user:password@cluster.mongodb.net/database?retryWrites=true&w=majority"
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "mat_extract_ai"
    use_mongodb: bool = True
    
    @field_validator('debug', mode='before')
    @classmethod
    def validate_debug(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return False
    
    @field_validator('use_mongodb', mode='before')
    @classmethod
    def validate_use_mongodb(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def upload_path(self) -> Path:
        """Get upload directory as Path object."""
        return Path(self.upload_dir)
    
    @property
    def results_path(self) -> Path:
        """Get results directory as Path object."""
        return Path(self.results_dir)
    
    @property
    def logs_path(self) -> Path:
        """Get logs directory as Path object."""
        return Path(self.logs_dir)


# Load settings from environment
settings = Settings()

# Create directories if they don't exist
settings.upload_path.mkdir(parents=True, exist_ok=True)
settings.results_path.mkdir(parents=True, exist_ok=True)
settings.logs_path.mkdir(parents=True, exist_ok=True)