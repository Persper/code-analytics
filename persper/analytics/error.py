
class Error(Exception):
    """Base class for other errors"""


class UnexpectedASTError(Error):
    """Raise for unexpected ast structure"""
    pass
