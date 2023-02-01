from enum import Enum


class Colors(Enum):
    """Enumeration that stores some colors."""
    # pylint: disable=invalid-name
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Magenta = 35
    Cyan = 36
    White = 37


class SIZE_UNIT(Enum):
    """Enumeration of computer size units."""
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4
    TB = 5


class Files(Enum):
    invoices = "invoices.csv"
    deliveries = "deliveries.csv"
    deliveries_not_working = "deliveries_not_working.csv"
    refunds = "refunds.csv"
    claims = "claims.csv"
    contract = "contract.csv"
    refunds_label_not_used = 'refunds_label_not_used.csv'



class BQParameterType(str, Enum):
    """
    Types of parameter which can be used in parameterized query.
    """
    # Sequence types
    ARRAY = "ARRAY"
    STRUCT = "STRUCT"
    GEOGRAPHY = "GEOGRAPHY"
    JSON = "JSON"
    
    # Scalar types
    BIGNUMERIC = "BIGNUMERIC"
    BOOL = "BOOL"
    BYTES = "BYTES"
    DATE = "DATE"	
    DATETIME = "DATETIME"	
    FLOAT64 = "FLOAT64"
    INT64 = "INT64"
    INTERVAL = "INTERVAL"
    NUMERIC = "NUMERIC"	
    STRING = "STRING"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"
