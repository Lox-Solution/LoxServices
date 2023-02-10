import os
import urllib.request
from datetime import date
from pathlib import Path
from functools import lru_cache
from typing import Final

import numpy as np
import numpy.typing as npt
import pandas as pd
from currency_converter import ECB_URL, CurrencyConverter


@lru_cache(maxsize=1)
def _make_currency_converter() -> CurrencyConverter:
    """Make a currency converter from currencyconverter PyPi which is guaranteed
    to update on a daily basis. To avoid computationally expensive call on each
    import from the module, this function is cached."""
    filename = Path(
        os.getenv("PYTHONPATH"),
        "lox_services",
        "utils",
        "ecb_currency_rates_archive",
        f"ecb_{date.today():%Y%m%d}.zip",
    )
    if not filename.is_file():
        urllib.request.urlretrieve(ECB_URL, filename.name)
    return CurrencyConverter(
        str(filename),
        fallback_on_missing_rate=True,
        fallback_on_missing_rate_method="last_known",  # NOQA
        fallback_on_wrong_date=True,
    )


CURRENCY_CONVERTER: Final = _make_currency_converter()


def column_to_euro(
    amount_col: pd.Series, currency_col: pd.Series, date_col: pd.Series
) -> npt.NDArray[np.float32]:

    """
    Given relevant columns, convert local currency values to euro row-wise.

        ## Arguments
        - `amount_col`: A pandas Series/column containing information about the quantity
        of currency.
        - `currency_col`: A pandas Series/column containing information about the kind
        of currency in ISO 4217 format.
        - `date_col`: A pandas Series/column containing information about the reference
        time period.

        ## Returns
        - A numpy array where local currency values are converted euro row-wise.
    """

    arr = np.array(
        [
            CURRENCY_CONVERTER.convert(col1, col2, "EUR", date=col3)
            for col1, col2, col3 in zip(
                amount_col.astype(float),
                currency_col,
                date_col,
            )
        ]
    )
    return np.round(arr, 2)
