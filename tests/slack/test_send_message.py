import unittest
from lox_services.slack.send_message import send_messages, tag_someone
from lox_services.utils.enums import SlackMemberID


class TestSlackSendMessages(unittest.TestCase):
    def test_send_messages(self):
        send_messages("test_message", "test_title")

    def test_tag_someone(self):
        tag = tag_someone(SlackMemberID.MELVIL)
        self.assertIn(SlackMemberID.MELVIL.value, tag)


if __name__ == "__main__":
    unittest.main()
