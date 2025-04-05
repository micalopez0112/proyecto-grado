class RepositoryException(Exception):
    """Base exception for repository errors."""
    pass

class EntityNotFoundException(RepositoryException):
    """Raised when an entity is not found."""
    pass
