# pylint: disable=missing-class-docstring missing-function-docstring
import unittest

from lox_services.email.utils import extract_emails_from_string


class Test_utils(unittest.TestCase):
    def test_extract_one_email(self):
        self.assertEqual(
            extract_emails_from_string("I am an email email@domain.com."),
            ["email@domain.com"],
        )


if __name__ == "__main__":
    unittest.main()
