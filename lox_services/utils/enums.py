from enum import Enum, IntEnum


class Colors(IntEnum):
    """Enumeration that stores some colors."""

    # pylint: disable=invalid-name
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class SIZE_UNIT(IntEnum):
    """Enumeration of computer size units."""

    BYTES = 1
    KB = 2
    MB = 3
    GB = 4
    TB = 5


class Files(str, Enum):
    INVOICES = "invoices.csv"
    DELIVERIES = "deliveries.csv"
    DELIVERIES_NOT_WORKING = "deliveries_not_working.csv"
    REFUNDS = "refunds.csv"
    CLAIMS = "claims.csv"
    CONTRACT = "contract.csv"
    REFUNDS_LABEL_NOT_USED = "refunds_label_not_used.csv"


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
