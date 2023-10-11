# pylint: disable=missing-class-docstring missing-function-docstring
import unittest
from unittest.mock import patch

from lox_services.emails.utils import (
    _command_to_url,
    extract_emails_from_string,
    get_google_client_id,
    get_google_client_secret,
    url_escape,
    url_format_params,
)


class TestUtils(unittest.TestCase):
    def test_extract_one_email(self):
        self.assertEqual(
            extract_emails_from_string("I am an email email@domain.com."),
            ["email@domain.com"],
        )

    def test_get_goole_client_id(self):
        self.assertIsInstance(get_google_client_id(), str)

    def test_get_goole_client_secret(self):
        self.assertIsInstance(get_google_client_secret(), str)

    def test__command_to_url(self):
        GOOGLE_ACCOUNTS_BASE_URL = "https://accounts.google.com"
        command = "some_command"
        expected_url = f"{GOOGLE_ACCOUNTS_BASE_URL}/{command}"
        result = _command_to_url(command)
        self.assertEqual(result, expected_url)

    def test_url_escape(self):
        text = "escape me !@#$"
        expected_escaped_text = "escape%20me%20%21%40%23%24"
        result = url_escape(text)
        self.assertEqual(result, expected_escaped_text)

    def test_url_format_params(self):
        params = {"param1": "value1", "param2": "value2", "param3": "value3"}
        expected_result = "param1=value1&param2=value2&param3=value3"
        result = url_format_params(params)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
