import os
import unittest
import json
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from google.cloud.bigquery import Client, DatasetReference
from pandas.testing import assert_frame_equal

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.utils import (
    equal_condition_handle_none_value,
    format_datetime,
    format_time,
    generate_id,
    make_temporary_table,
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

    def test_make_temporary_table(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
        with open(SERVICE_ACCOUNT_PATH, "r", encoding="utf-8") as file:
            table_name = json.load(file)["project_id"]
        client = Client()

        make_temporary_table(
            pd.util.testing.makeDataFrame(),
            table_name,
            "Mapping",
            "UnitTest",
        )

        table_ref = DatasetReference(table_name, "Mapping").table("UnitTest")
        table_ref = client.get_table(table_ref)
        self.assertLess(
            (datetime.now(timezone.utc) + timedelta(hours=1)) - table_ref.expires,
            timedelta(seconds=1),
        )
