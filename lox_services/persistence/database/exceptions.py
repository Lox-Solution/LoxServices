"""Database exceptions."""

class DatabaseException(Exception):
    """Base class for all database exceptions."""
    pass

class BadQueryTypeException(DatabaseException):
    """Raised when the given query is not from the good type.

        ## Constructor arguments
        
        - `query_type` (str): the type of the query        
    """
    def __init__(self, query_type):
        self.query_type = query_type.upper()
        super().__init__(f"The query must start with '{query_type}'.")
        
        
class MissingUpdateDatetimeException(DatabaseException):
    """Raised when the update_datetime is not set in update query

        ## Constructor arguments
        
        - `query_type` (str): the type of the query        
    """
    def __init__(self, query):
        self.query = query
        super().__init__(f"""INCORRECT UPDATE
        ----
        {query}
        -----
        the query must update the field update_datetime .""")


class InvalidDataException(DatabaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


"""Dataframe exceptions."""

class DataFrameException(Exception):
    """Base class for all dataframe exceptions."""
    pass

class MissingColumnsException(DataFrameException):
    """Raised when a required column is missing in a given dataframe.

        ## Constructor arguments
        
        - `query_type` (str): the missing column's name       
    """
    def __init__(self, column_name):
        self.column_name = column_name
        super().__init__(f"Missing required columns: '{column_name}'.")
