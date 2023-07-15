import unittest

from lox_services.persistence.database.schema import (
    dtypes_invoices,
    na_invoices,
    dates_invoices,
    dtypes_deliveries,
    na_deliveries,
    dates_deliveries,
    dtypes_refunds,
    na_refunds,
    dates_refunds,
)


class TestDataType(unittest.TestCase):
    def test_invoices_na(self):
        # Check that all values in the dictionary are not None
        for key, value in na_invoices.items():
            self.assertIsNotNone(value)

    def test_invoices_dates(self):
        # Check that all the values in dates_invoices are in dtypes_invoices
        for date in dates_invoices:
            self.assertIn(date, dtypes_invoices)

    def test_deliveries_dtypes(self):
        # Check that all values in the dictionary are not None
        for key, value in dtypes_deliveries.items():
            self.assertIsNotNone(value)

    def test_deliveries_na(self):
        # Check that all values in the dictionary are not None
        for key, value in na_deliveries.items():
            self.assertIsNotNone(value)

    def test_deliveries_dates(self):
        # Check that all the values in dates_deliveries are in dtypes_deliveries
        for date in dates_deliveries:
            self.assertIn(date, dtypes_deliveries)

    def test_refunds_na(self):
        # Check that all values in the dictionary are not None
        for key, value in na_refunds.items():
            self.assertIsNotNone(value)

    def test_refunds_dates(self):
        # Check that all the values in dates_refunds are in dtypes_refunds
        for date in dates_refunds:
            self.assertIn(date, dtypes_refunds)


if __name__ == "__main__":
    unittest.main()
