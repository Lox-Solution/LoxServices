import unittest
from lox_services.config.env_variables import get_env_variable
from lox_services.slack.send_message import send_messages, tag_someone
from lox_services.utils.enums import SlackMemberID
from mock import patch


class TestSlackSendMessages(unittest.TestCase):
    def test_send_messages(self):
        # Check that the function works using a test slack channel
        with patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
                "RUNS_REPORTS": get_env_variable("RUNS_REPORTS_TEST"),
            },
        ):
            send_messages("test_message", "test_title")

        with patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "development",
                "RUNS_REPORTS_DEV": get_env_variable("RUNS_REPORTS_TEST"),
            },
        ):
            send_messages("test_message", "test_title")

    def test_tag_someone(self):
        tag = tag_someone(SlackMemberID.MELVIL)
        self.assertIn(SlackMemberID.MELVIL.value, tag)


if __name__ == "__main__":
    unittest.main()
