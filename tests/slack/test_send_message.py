import json
import requests
import unittest
from unittest.mock import patch

from lox_services.slack.send_message import send_messages, tag_someone
from lox_services.utils.enums import SlackMemberID


class TestSlackFunctions(unittest.TestCase):
    def test_send_messages(self):
        # Call the function
        send_messages(
            "This is a test to make sure the Slack connection is working.", "Unit test:"
        )

        # If the function passed, then it work
        self.assertTrue(True)

    def test_tag_someone(self):
        # Call the function
        test_person = SlackMemberID.ISIS
        result = tag_someone(test_person)

        # Assertion
        expected_result = "<@" + test_person.value + ">"
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
