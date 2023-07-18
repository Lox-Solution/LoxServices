import unittest
from lox_services.utils.metadata import get_function_callers
from unittest.mock import patch


def f1():
    return get_function_callers()


def f2():
    return f1()


def f3():
    return f2()


class TestGetFunctionCallers(unittest.TestCase):
    def test_get_function_callers(self):
        # Case 1: Function caller is none
        with patch("inspect.currentframe") as mock_current_frame:
            # Set the mock return value to None
            mock_current_frame.return_value = None

            # Call the function and assert that it returns None
            result = get_function_callers()
            self.assertIsNone(result)

        # Case 2: Function caller is f1
        callers = f1()
        self.assertIn("f1", callers)


if __name__ == "__main__":
    unittest.main()
