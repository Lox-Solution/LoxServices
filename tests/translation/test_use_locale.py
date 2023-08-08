import datetime
import locale
import os
import subprocess
import unittest
from unittest.mock import patch
from lox_services.translation.use_locale import (
    get_all_locales,
    use_locale,
    download_locale,
)


class TestLocaleFunctions(unittest.TestCase):
    def setUp(self):
        self.right_language_code = "ru_RU"
        self.right_encoding = "utf8"
        self.right_encoding_uppercase = "UTF-8"
        self.wrong_language_code = "wrong_WRONG"

    def test_get_all_locales(self):
        # Call the function
        result = get_all_locales()

        # Assertions
        self.assertIsInstance(result, dict)
        self.assertTrue(len(result) > 0)

    def test_download_locale(self):
        # Test 1: language_code is not downloadble
        with self.assertRaises(Exception):
            download_locale(self.wrong_language_code, self.right_encoding)

        # Test 2: language_code is downloadble
        download_locale(self.right_language_code, self.right_encoding)

        # Get the list of installable locales after calling the function
        locales_after = set(locale.locale_alias.keys())
        print(locales_after)

        # Assertions
        # Check if the new locale is added to the list of installable locales
        self.assertTrue(self.right_language_code.lower() in locales_after)

    def test_use_locale_successful(self):
        # Test 1: language_code is not installable
        with self.assertRaises(Exception):
            download_locale(self.wrong_language_code, self.right_encoding)

        # Test 2: language_code is not installable
        use_locale(self.right_language_code, self.right_encoding_uppercase)

        # Get the current locale setting
        current_locale = locale.setlocale(locale.LC_TIME)

        # Assertions
        # Check if the current locale is set to the expected language and encoding
        expected_locale = f"{self.right_language_code}.{self.right_encoding_uppercase}"
        self.assertEqual(current_locale, expected_locale)

    @patch("lox_services.translation.use_locale.download_locale")
    def test_use_locale_unsuccessful(self, mock_download_locale):
        # Set up the mock to return without raising an exception
        mock_download_locale.return_value = None

        # Call the function and expect an exception
        with self.assertRaises(Exception) as context:
            use_locale(self.wrong_language_code, self.right_encoding_uppercase)

        self.assertIn(
            f"Locale '{self.wrong_language_code}' is installed but the current process is not aware of it.",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
