class MappingRepositoryException(Exception):
    """Base exception for mapping repository errors."""
    pass

class EntityNotFoundException(MappingRepositoryException):
    """Raised when a mapping is not found."""
    pass

class CreateMappingError(MappingRepositoryException):
    """Raised when there's an error creating a mapping."""
    pass

class UpdateMappingError(MappingRepositoryException):
    """Raised when there's an error updating a mapping."""
    pass

class DeleteMappingError(MappingRepositoryException):
    """Raised when there's an error deleting a mapping."""
    pass

class QueryError(MappingRepositoryException):
    """Raised when there's an error executing a query."""
    pass

class ValidationError(MappingRepositoryException):
    """Raised when there's an error validating a mapping."""
    pass