import os
import unittest
import json
from datetime import datetime, timedelta, timezone

import pandas as pd
from google.cloud.bigquery import Client, DatasetReference

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.utils import (
    make_temporary_table,
    validate_iso3166_2,
)


class TestDatabaseFunctions(unittest.TestCase):
    def test_make_temporary_table(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
        with open(SERVICE_ACCOUNT_PATH, "r", encoding="utf-8") as file:
            project_id = json.load(file)["project_id"]
        client = Client()

        make_temporary_table(
            pd.util.testing.makeDataFrame(),
            project_id,
            "Mapping",
            "UnitTest",
        )

        table_ref = DatasetReference(project_id, "Mapping").table("UnitTest")
        table_ref = client.get_table(table_ref)
        self.assertLess(
            (datetime.now(timezone.utc) + timedelta(hours=1)) - table_ref.expires,
            timedelta(seconds=1),
        )


class TestValidateISO31662(unittest.TestCase):
    def setUp(self):
        # Create a DataFrame for testing
        self.df = pd.DataFrame(
            {
                "country_code": [
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
                ]
            }
        )

    def test_validate_iso3166_2_with_valid_codes(self):
        # Test the function with valid ISO-3166-2 country codes
        self.assertIsNone(validate_iso3166_2(self.df, "country_code"))

    def test_validate_iso3166_2_with_invalid_codes(self):
        # Test the function with invalid ISO-3166-2 country codes
        self.df.loc[3, "country_code"] = "GB1"
        with self.assertRaises(ValueError):
            validate_iso3166_2(self.df, "country_code")

    def test_validate_iso3166_2_with_missing_values(self):
        # Test the function with missing values in the country code column
        self.df.loc[4, "country_code"] = pd.NA
        self.assertIsNone(validate_iso3166_2(self.df, "country_code"))

    def test_validate_iso3166_2_with_nonexistent_country_code_column(self):
        # Test the function with a non-existent country code column
        with self.assertRaises(KeyError):
            validate_iso3166_2(self.df, "invalid_column_name")
