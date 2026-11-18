class BounceLayerError(Exception):
    """Base exception for all BounceLayer SDK errors."""
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(BounceLayerError):
    """Raised when the API key is missing or invalid."""
    pass


class InsufficientCreditsError(BounceLayerError):
    """Raised when the account balance has 0 credits."""
    pass


class RateLimitError(BounceLayerError):
    """Raised when API rate limits are exceeded."""
    pass
