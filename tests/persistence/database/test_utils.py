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


class TestUtilsDatabaseFunctions(unittest.TestCase):
    def test_generate_id(self):
        self.assertEqual(
            generate_id(["invoice", "date", "amount"]), "invoice_date_amount"
        )
        self.assertEqual(
            generate_id(["invoice", "date", "amount", None]), "invoice_date_amount_null"
        )
        self.assertRaises(Exception, generate_id, [])

    def test_replace_nan_with_none_in_dataframe(self):
        mock_df = pd.DataFrame(
            np.array([["1", np.NaN, None], ["5", "6", np.NaN], ["8", "9", np.NaN]]),
            columns=["a", "b", "c"],
        )

        df = replace_nan_with_none_in_dataframe(mock_df)
        mock_df_out = pd.DataFrame(
            np.array([["1", None, None], ["5", "6", None], ["8", "9", None]]),
            columns=["a", "b", "c"],
        )

        assert_frame_equal(df, mock_df_out)

    def test_format_time(self):
        # Case 1: Time is Na
        self.assertEqual(format_time(np.NaN), "00:00:00")

        # Case 2: Time that is missing a leading 0
        self.assertEqual(format_time("9:45:00"), "09:45:00")

        # Case 3: "%H:%M" time format
        self.assertEqual(format_time("09:45"), "09:45:00")

        # Case 4: "%H:%M:%S" time format
        self.assertEqual(format_time("09:45:00"), "09:45:00")

        # Case 5: Wront time format
        self.assertEqual(format_time("45:45:45"), "00:00:00")

    def test_format_datetime(self):
        # Case 1: Date and time have the right format
        self.assertEqual(format_datetime("12-12-2020", "12:00"), "12-12-2020T12:00")

        # Case 2: Date is Na
        self.assertTrue(pd.isnull(format_datetime(np.NaN, "12:00")))

        # Case 3: Time is Na
        self.assertTrue(pd.isnull(format_datetime("12-12-2020", np.NaN)))

    def test_equal_condition_handle_none_value(self):
        # Case 1: Value is None
        self.assertEqual(
            equal_condition_handle_none_value("label", None), "label is null"
        )
        # Case 2: Value is not None
        self.assertEqual(
            equal_condition_handle_none_value("account", "123456"), 'account = "123456"'
        )


if __name__ == "__main__":
    unittest.main()
