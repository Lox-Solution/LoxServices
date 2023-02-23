import os
import unittest
import json
from datetime import datetime, timedelta, timezone

import pandas as pd
from google.cloud.bigquery import Client, DatasetReference

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.utils import make_temporary_table


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
