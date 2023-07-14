import unittest

from lox_services.utils.decorators import Perf, LogArguments, DataUsage, VirtualDisplay
from typing import Callable


# Sample function to be decorated
def sample_function():
    print("Inside the sample function")


class TestDecorators(unittest.TestCase):
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
        # Define the decorated function using the VirtualDisplay decorator
        @VirtualDisplay
        def decorated_function():
            sample_function()

        # Call the decorated function
        decorated_function()

        # Assert statements for VirtualDisplay decorator
        self.assertTrue(isinstance(decorated_function, Callable))


if __name__ == "__main__":
    unittest.main()
