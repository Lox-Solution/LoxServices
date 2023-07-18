import unittest
import requests
from lox_services.config.env_variables import get_env_variable


class TestBrightDataProxyManager(unittest.TestCase):
    def test_get_env_variable(self):
        # Test case 1: Get the value of an existing environment variable
        result = get_env_variable("ENVIRONMENT")

        self.assertIsInstance(result, str)
        self.assertIn(result, ["development", "production"])
        self.assertTrue(len(result) > 0)

        # Test case 2: Get the value of an non existing environment variable
        with self.assertRaises(ValueError):
            result = get_env_variable("wrong_key")


if __name__ == "__main__":
    unittest.main()
