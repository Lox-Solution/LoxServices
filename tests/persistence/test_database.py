import os
import unittest
import json
from datetime import datetime, timedelta, timezone

import pandas as pd
import pandas.testing as pdt
from google.cloud.bigquery import Client, DatasetReference

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.utils import (
    make_temporary_table,
    validate_country_code,
)
from lox_services.persistence.database.insert import remove_duplicate_headers_dataframe


class TestDatabaseFunctions(unittest.TestCase):
    # def test_make_temporary_table(self):
    #     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
    #     with open(SERVICE_ACCOUNT_PATH, "r", encoding="utf-8") as file:
    #         project_id = json.load(file)["project_id"]
    #     client = Client()

    #     make_temporary_table(
    #         pd.util.testing.makeDataFrame(),
    #         project_id,
    #         "Mapping",
    #         "UnitTest",
    #     )

    #     table_ref = DatasetReference(project_id, "Mapping").table("UnitTest")
    #     table_ref = client.get_table(table_ref)
    #     self.assertLess(
    #         (datetime.now(timezone.utc) + timedelta(hours=1)) - table_ref.expires,
    #         timedelta(seconds=1),
    #     )

    def test_remove_duplicate_headers_dataframe(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["foo", "bar", "baz"]})

        expected_output = pd.DataFrame({"A": [1, 2, 3], "B": ["foo", "bar", "baz"]})
        pdt.assert_frame_equal(
            remove_duplicate_headers_dataframe(df).reset_index(drop=True),
            expected_output.reset_index(drop=True),
        )

        # Test with a dataframe that has duplicate headers
        df_dup = pd.DataFrame(
            {"A": ["A", "B", "C"], "B": ["B", "B", "C"], "C": ["C", "B", "C"]}
        )
        expected_output_dup = pd.DataFrame(
            {"A": ["B", "C"], "B": ["B", "C"], "C": ["B", "C"]}
        )
        pdt.assert_frame_equal(
            remove_duplicate_headers_dataframe(df_dup).reset_index(drop=True),
            expected_output_dup.reset_index(drop=True),
        )

        # Test with a dataframe that has a header row in the middle of the dataframe
        df_middle = pd.DataFrame(
            {
                "A": ["1", "A", "2", "3", "A", "A"],
                "B": ["foo", "B", "bar", "baz", "B", "B"],
                "C": ["4", "C", "5", "6", "C", "C"],
                "D": ["qux", "D", "quux", "corge", "D", "Z"],
            }
        )
        expected_output_middle = pd.DataFrame(
            {
                "A": ["1", "2", "3", "A"],
                "B": ["foo", "bar", "baz", "B"],
                "C": ["4", "5", "6", "C"],
                "D": ["qux", "quux", "corge", "Z"],
            }
        )
        pdt.assert_frame_equal(
            remove_duplicate_headers_dataframe(df_middle).reset_index(drop=True),
            expected_output_middle.reset_index(drop=True),
        )


class TestValidateISO31662(unittest.TestCase):
    def setUp(self):
        # Create a DataFrame for testing
        self.df = pd.DataFrame(
            {
                "country_code_1": [
                    "US",
                    "CA",
                    "MX",
                    "GB",
                    "FR",
                    "JP",
                    "CN",
                    "IN",
                    "BR",
                    "AU",
                ],
                "country_code_2": [
                    "GB",
                    "FR",
                    "JP",
                    "CN",
                    "IN",
                    "BR",
                    "AU",
                    "US",
                    "CA",
                    "MX",
                ],
            }
        )

    def test_validate_country_code_with_valid_codes(self):
        # Test the function with valid ISO-3166-2 country codes
        self.assertIsNone(validate_country_code(self.df, "country_code_1"))
        self.assertIsNone(
            validate_country_code(self.df, ["country_code_1", "country_code_2"])
        )

    def test_validate_country_code_with_invalid_codes(self):
        # Test the function with invalid ISO-3166-2 country codes
        self.df.loc[3, "country_code_1"] = "GB1"
        self.df.loc[2, "country_code_2"] = "CA1"
        with self.assertRaises(ValueError):
            validate_country_code(self.df, "country_code_1")
        with self.assertRaises(ValueError):
            validate_country_code(self.df, ["country_code_1", "country_code_2"])

    def test_validate_country_code_with_missing_values(self):
        # Test the function with missing values in the country code column
        self.df.loc[4, "country_code_1"] = pd.NA
        self.df.loc[2, "country_code_2"] = pd.NA
        self.assertIsNone(validate_country_code(self.df, "country_code_1"))
        self.assertIsNone(
            validate_country_code(self.df, ["country_code_1", "country_code_2"])
        )

    def test_validate_country_code_with_nonexistent_country_code_column(self):
        # Test the function with a non-existent country code column
        with self.assertRaises(KeyError):
            validate_country_code(self.df, "invalid_column_name")
