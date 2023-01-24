from typing import Final

import numpy as np
import numpy.typing as npt
import pandas as pd
from currency_converter import ECB_URL, CurrencyConverter

CURRENCY: Final = CurrencyConverter(
    ECB_URL,
    fallback_on_missing_rate=True,
    fallback_on_missing_rate_method="last_known",  # NOQA
    fallback_on_wrong_date=True,
)


def column_to_euro(
    amount_col: pd.Series, currency_col: pd.Series, date_col: pd.Series
) -> npt.NDArray[np.float32]:
    """Given relevant columns, convert local currency values to euro row-wise."""

    arr = np.array(
        [
            CURRENCY.convert(col1, col2, "EUR", date=col3)
            for col1, col2, col3 in zip(
                amount_col.astype(float),
                currency_col,
                date_col,
            )
        ]
    )
    return np.round(arr, 2)
