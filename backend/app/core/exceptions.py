"""Custom exception classes for the application."""


class MatExtractException(Exception):
    """Base exception for all MatExtract errors."""
    pass


class PDFUploadError(MatExtractException):
    """Raised when PDF upload or validation fails."""
    pass


class ExtractionError(MatExtractException):
    """Raised when PDF extraction fails."""
    pass


class AgentError(MatExtractException):
    """Raised when LLM agent processing fails."""
    pass


class ValidationError(MatExtractException):
    """Raised when result validation fails."""
    pass


class JobNotFoundError(MatExtractException):
    """Raised when job ID doesn't exist."""
    pass


class FileOperationError(MatExtractException):
    """Raised when file operations fail."""
    pass


class DatabaseError(MatExtractException):
    """Raised when database operations fail."""
    pass
