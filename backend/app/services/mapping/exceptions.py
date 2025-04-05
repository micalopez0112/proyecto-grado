class MappingServiceException(Exception):
    """Base exception for mapping service errors."""
    pass

class MappingValidationError(MappingServiceException):
    """Raised when a mapping fails validation."""
    pass

class MappingNotFoundError(MappingServiceException):
    """Raised when a mapping is not found."""
    pass

class InvalidMappingDataError(MappingServiceException):
    """Raised when mapping data is invalid."""
    pass
