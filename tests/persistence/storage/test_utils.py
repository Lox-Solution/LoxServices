import unittest
from lox_services.persistence import config
from lox_services.persistence.storage import constants
from lox_services.persistence.storage.utils import (
    generate_invoice_storage_url,
    extract_tracking_number_from_file_storage_name,
    use_environment_bucket,
)


class YourModuleTests(unittest.TestCase):
    def test_generate_invoice_storage_url(self):
        url = generate_invoice_storage_url("test", "UPS", "XX00000XX")
        expected_url = "https://storage.cloud.google.com/invoices_clients/test/Invoices/UPS/XX00000XX.pdf"
        self.assertEqual(url, expected_url)

    def test_extract_tracking_number_from_file_storage_name(self):
        tracking_number = extract_tracking_number_from_file_storage_name(
            "/path/to/XX00000XX.pdf"
        )
        expected_tracking_number = "XX00000XX"
        self.assertEqual(tracking_number, expected_tracking_number)

    def test_use_environment_bucket(self):
        # Case 1: Bucket name is not None and in development
        bucket_name = use_environment_bucket("test_bucket")
        expected_bucket_name = "test_bucket_development"
        self.assertEqual(bucket_name, expected_bucket_name)

        # Case 2: Bucket name is None
        with self.assertRaises(ValueError):
            use_environment_bucket(None)

    def tearDown(self):
        config.ENVIRONMENT = "production"


if __name__ == "__main__":
    unittest.main()
