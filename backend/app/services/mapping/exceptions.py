class MappingValidationError(Exception):
    """Exception raised when a mapping validation fails."""
    pass

class MappingNotFoundError(Exception):
    """Exception raised when a mapping is not found."""
    pass

class InvalidMappingDataError(Exception):
    """Exception raised when mapping data is invalid."""
    pass