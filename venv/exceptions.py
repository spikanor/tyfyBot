class Error(Exception):
    """Base class for other exceptions"""
    pass

class NotFoundError(Error):
    """Raised when something is not found in guild config"""
    pass