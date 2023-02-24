import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from lox_services.persistence.database.utils import (
    equal_condition_handle_none_value,
    format_datetime,
    format_time,
    generate_id,
    replace_nan_with_none_in_dataframe,
)

label = None
account = "123456"
mock_df = pd.DataFrame(
    np.array([["1", np.NaN, None], ["5", "6", np.NaN], ["8", "9", np.NaN]]),
    columns=["a", "b", "c"],
)
df = replace_nan_with_none_in_dataframe(mock_df)
mock_df_out = pd.DataFrame(
    np.array([["1", None, None], ["5", "6", None], ["8", "9", None]]),
    columns=["a", "b", "c"],
)


class TestDatabaseFunctions(unittest.TestCase):
    def test_utils_functions(self):
        self.assertEqual(
            generate_id(["invoice", "date", "amount"]), "invoice_date_amount"
        )
        self.assertRaises(Exception, generate_id, [])
        self.assertEqual(format_time("21:00"), "21:00:00")
        self.assertEqual(format_datetime("12-12-2020", "12:00"), "12-12-2020T12:00")
        self.assertEqual(
            equal_condition_handle_none_value("label", label), "label is null"
        )
        self.assertEqual(
            equal_condition_handle_none_value("account", account), 'account = "123456"'
        )
        assert_frame_equal(mock_df, mock_df_out)
