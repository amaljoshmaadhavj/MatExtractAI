"""Response models for API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class JobStatusResponse(BaseModel):
    """Response model for job status endpoint."""
    
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Job status: processing, completed, failed")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    current_step: str = Field("", description="Current processing step")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    estimated_completion: Optional[int] = Field(None, description="Estimated seconds until completion")
    error_message: Optional[str] = Field(None, description="Error message if status is failed")


class ResultsResponse(BaseModel):
    """Response model for results endpoint."""
    
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    sections: Dict[str, str] = Field(default_factory=dict, description="Extracted document sections")
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted tables")
    mechanical_properties: Dict[str, Any] = Field(default_factory=dict, description="Agent extraction results")
    composition: Dict[str, Any] = Field(default_factory=dict, description="Agent extraction results")
    processing: Dict[str, Any] = Field(default_factory=dict, description="Agent extraction results")
    microstructure: Dict[str, Any] = Field(default_factory=dict, description="Agent extraction results")
    validation: Dict[str, Any] = Field(default_factory=dict, description="Validation and confidence scores")
    
    # NEW: Consolidated material records from Master Agent
    material_records: List[Dict[str, Any]] = Field(default_factory=list, description="Consolidated material records from consolidation agent")
    consolidation_status: str = Field("not_run", description="Status of consolidation (not_run, success, partial, failed)")
    conflict_report: Dict[str, Any] = Field(default_factory=dict, description="Conflict detection and resolution results")


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    error_code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Detailed error information")


class JobModel(BaseModel):
    """Model for job metadata storage."""
    
    id: str = Field(..., description="Job ID")
    filename: str = Field(..., description="Uploaded filename")
    status: str = Field("processing", description="Current status")
    progress: int = Field(0, description="Progress percentage")
    current_step: str = Field("", description="Current processing step")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")
    error_message: Optional[str] = Field(None, description="Error if any")
    
    class Config:
        from_attributes = True
