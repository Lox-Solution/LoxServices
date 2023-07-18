import unittest
from lox_services.utils.fake_name import _closure_make_french_name, make_french_name


class TestMakeFrenchName(unittest.TestCase):
    def test_make_french_name(self):
        # Create an instance of the closure function
        make_french_name_func = _closure_make_french_name()

        # Call the make_french_name function and get the result
        result = make_french_name_func()

        # Perform assertions to verify the result
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")

    def test_make_french_name_global(self):
        # Call the make_french_name global function
        result = make_french_name()

        # Perform assertions to verify the result
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")


if __name__ == "__main__":
    unittest.main()
