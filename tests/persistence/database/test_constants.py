import unittest

from lox_services.persistence.database.constants import (
    BQ_CURRENT_DATE,
    BQ_CURRENT_DATETIME,
)


class TestBigQueryExpressions(unittest.TestCase):
    def test_bq_current_date(self):
        expected_expression = "CURRENT_DATE('Europe/Amsterdam')"
        self.assertEqual(BQ_CURRENT_DATE, expected_expression)

    def test_bq_current_datetime(self):
        expected_expression = "CURRENT_DATETIME('Europe/Amsterdam')"
        self.assertEqual(BQ_CURRENT_DATETIME, expected_expression)


if __name__ == "__main__":
    unittest.main()
