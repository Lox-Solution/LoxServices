import unittest
from lox_services.config.env_variables import get_env_variable
from lox_services.slack.send_message import send_messages, tag_someone
from lox_services.utils.enums import SlackMemberID
from mock import patch


class TestSlackSendMessages(unittest.TestCase):
    def test_send_messages_production(self):
        # Case 1: Mock production environment
        with patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "production",
                "RUNS_REPORTS": get_env_variable("RUNS_REPORTS_TEST"),
            },
        ):
            send_messages("test_message", "test_title")

    def test_send_messages_development(self):
        # Case 2: Mock development environment
        with patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "development",
                "RUNS_REPORTS_DEV": get_env_variable("RUNS_REPORTS_TEST"),
            },
        ):
            send_messages("test_message", "test_title")

    @patch("requests.post")  # Mocking the requests.post function
    def test_send_messages_development(self, mock_post):
        # Case 3: Mock Exception
        with patch.dict(
            "os.environ",
            {
                "ENVIRONMENT": "development",
                "RUNS_REPORTS_DEV": get_env_variable("RUNS_REPORTS_TEST"),
            },
        ):
            mock_response = mock_post.return_value
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            # Call the function under test and expect it to raise an exception
            with self.assertRaises(Exception) as context:
                send_messages("Title", "Message")

            # Assert that the exception contains the correct status code and response text
            self.assertEqual(context.exception.args, (500, "Internal Server Error"))

    def test_tag_someone(self):
        tag = tag_someone(SlackMemberID.MELVIL)
        self.assertIn(SlackMemberID.MELVIL.value, tag)


if __name__ == "__main__":
    unittest.main()
