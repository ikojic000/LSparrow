"""
Custom exception classes for the application.
"""


class AppException(Exception):
    """Base exception class for application-specific errors."""
    
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.__class__.__name__
        rv['message'] = self.message
        return rv


class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)


class FileProcessingError(AppException):
    """Raised when file processing fails."""
    
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=422, payload=payload)


class UnsupportedEncodingError(FileProcessingError):
    """Raised when a file cannot be decoded with any supported encoding."""
    
    def __init__(self, message="Could not read file with any supported encoding"):
        super().__init__(message)


class InvalidFileFormatError(FileProcessingError):
    """Raised when the file format is invalid or unsupported."""
    
    def __init__(self, message="Invalid or unsupported file format"):
        super().__init__(message)


class NoLikertDataError(FileProcessingError):
    """Raised when no Likert scale data is found in the file."""
    
    def __init__(self, message="No questions with 1-5 scale answers found"):
        super().__init__(message)
