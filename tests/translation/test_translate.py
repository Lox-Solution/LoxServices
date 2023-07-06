import unittest
import os

from lox_services.translation.translate import get_translations
from lox_services.translation.enums import TranslationModules


class TestTranslations(unittest.TestCase):
    def test_get_translations_existing_language(self):
        # Define test inputs
        language = "FR"

        # Call the function
        translations = get_translations(language, TranslationModules.BILLING_EMAIL)

        # Assertions
        # Check if the returned value is a dictionary
        self.assertIsInstance(translations, dict)
        # Check if the dictionary is not empty
        self.assertTrue(len(translations) > 0)

    def test_get_translations_non_existing_language(self):
        # Define test inputs
        language = "DE"

        # Call the function
        translations = get_translations(language, TranslationModules.BILLING_EMAIL)

        # Assertions
        # Check if the returned value is a dictionary
        self.assertIsInstance(translations, dict)
        # Check if the dictionary is not empty
        self.assertTrue(len(translations) > 0)

    def test_get_translations_non_existing_module(self):
        # Define test inputs
        language = "FR"

        # Call the function
        with self.assertRaises(Exception):
            get_translations(language, "non_existing_module")

    def test_get_translations_strict_mode(self):
        # Define test inputs
        language = "DE"
        module = "ROOT"

        # Call the function with strict mode enabled
        with self.assertRaises(Exception):
            get_translations(language, module, strict=True)


if __name__ == "__main__":
    unittest.main()
