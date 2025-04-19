class OntologyNotFoundError(Exception):
    """Raised when an ontology is not found."""
    pass

class OntologyValidationError(Exception):
    """Raised when there's a validation error with the ontology."""
    pass

class InvalidOntologyDataError(Exception):
    """Raised when the ontology data is invalid."""
    pass
