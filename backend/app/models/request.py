"""Request models for API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional


class UploadPDFRequest(BaseModel):
    """Request model for PDF upload endpoint."""
    
    extraction_mode: str = Field("full", description="Extraction mode: 'full' or 'quick'")
    include_validation: bool = Field(True, description="Include validation and confidence scoring")


class ExtractionParams(BaseModel):
    """Parameters for extraction configuration."""
    
    extraction_mode: str = "full"
    include_tables: bool = True
    include_agents: bool = True
    include_validation: bool = True
