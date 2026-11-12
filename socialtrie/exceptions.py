class DomainError(Exception):
    """Base class for expected business-rule errors."""
class EntityNotFoundError(DomainError): pass
class InactiveUserError(DomainError): pass
class DeletedPostError(DomainError): pass
class DuplicateBannedWordError(DomainError): pass
class ValidationError(DomainError): pass
