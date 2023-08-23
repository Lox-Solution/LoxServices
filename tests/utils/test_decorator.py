import os
import unittest
from unittest.mock import patch
from lox_services.config.env_variables import get_env_variable

from lox_services.utils.decorators import (
    Perf,
    LogArguments,
    DataUsage,
    VirtualDisplay,
    retry,
    production_environment_only,
)

from typing import Callable


# Sample function to be decorated
def sample_function():
    print("Inside the sample function")


class TestDecorators(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "ENVIRONMENT": "production",
        },
    )
    def test_production_environment(self):
        @production_environment_only
        def sample_function2():
            return "Expected result"

        result = sample_function2()
        self.assertEqual(result, "Expected result")

    @patch.dict(
        "os.environ",
        {
            "ENVIRONMENT": "development",
        },
    )
    def test_production_environment_in_dev(self):
        @production_environment_only
        def sample_function2():
            return "Expected result"

        self.assertRaises(RuntimeError, sample_function2)

    def test_perf_decorator(self):
        # Define the decorated function using the Perf decorator
        @Perf
        def decorated_function():
            sample_function()

        # Call the decorated function
        decorated_function()

        # Assert statements for Perf decorator
        self.assertTrue(isinstance(decorated_function, Callable))

    def test_log_arguments_decorator(self):
        # Define the decorated function using the LogArguments decorator
        @LogArguments
        def decorated_function():
            sample_function()

        # Call the decorated function
        decorated_function()

        # Assert statements for LogArguments decorator
        self.assertTrue(isinstance(decorated_function, Callable))

    def test_data_usage_decorator(self):
        # Define the decorated function using the DataUsage decorator
        @DataUsage
        def decorated_function():
            sample_function()

        # Call the decorated function
        decorated_function()

        # Assert statements for DataUsage decorator
        self.assertTrue(isinstance(decorated_function, Callable))

    def test_virtual_display_decorator(self):
        # Case 1: Not in production
        current_environment = os.environ.get("ENVIRONMENT")

        os.environ["ENVIRONMENT"] = "development"

        # Define the decorated function using the VirtualDisplay decorator
        @VirtualDisplay
        def decorated_function():
            sample_function()

        # Call the decorated function
        decorated_function()

        # Assert statements for VirtualDisplay decorator
        self.assertTrue(isinstance(decorated_function, Callable))

        # Case 2: In production
        os.environ["ENVIRONMENT"] = "production"

        @VirtualDisplay
        def decorated_function_2():
            sample_function()

        # Call the decorated function
        decorated_function_2()

        # Assert statements for VirtualDisplay decorator
        self.assertTrue(isinstance(decorated_function_2, Callable))

        # Reset the environment variable
        os.environ["ENVIRONMENT"] = current_environment

    def test_retry_decorator(self):
        # Test variables
        retries = 3
        delay = 1

        # Custom exception for testing
        class CustomException(Exception):
            pass

        # Example function to be decorated
        @retry(max_attempts=retries, exceptions_handled=(CustomException,), delay=delay)
        def example_function():
            raise CustomException("Example exception")

        # Perform the test
        with self.assertRaises(CustomException):
            example_function()

        # Assertion
        self.assertEqual(example_function.__name__, "wrapper")


if __name__ == "__main__":
    unittest.main()
