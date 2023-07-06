import unittest

from lox_services.translation.templates import insert_variables


class TestInsertVariables(unittest.TestCase):
    def test_insert_variables(self):
        # Define test inputs
        translations = {
            "subject": "Lox Invoice - {company}: {month} {year}",
            "title": "Lox Invoice - {month} {year}",
            "entrance_greetings": "Dear {company},",
        }
        variables = {
            "company": "Lox",
            "month": "March",
            "year": "2022",
        }

        # Call the function
        translations_with_variables = insert_variables(translations, **variables)

        # Assertions
        expected_result = {
            "subject": "Lox Invoice - Lox: March 2022",
            "title": "Lox Invoice - March 2022",
            "entrance_greetings": "Dear Lox,",
        }
        self.assertEqual(translations_with_variables, expected_result)


if __name__ == "__main__":
    unittest.main()
