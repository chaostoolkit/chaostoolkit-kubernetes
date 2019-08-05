class NoDataError(Exception):
    """Raised when the no data is found from the given source"""
    pass

class DataRetrievingError(Exception):
    """Raised when the data cannot be retrieved from the given source"""
    pass