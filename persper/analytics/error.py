
class Error(Exception):
    """Base class for other errors"""
    pass


class GraphServerError(Error):
    """Base class for all `GraphServer` errors"""
    pass


class UnexpectedASTError(GraphServerError):
    """Raise for unexpected ast structure"""
    pass
