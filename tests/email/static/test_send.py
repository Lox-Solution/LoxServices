import os
import unittest
import requests
from lox_services.email.static.send import send_email_via_postmark
from tests import OUTPUT_FOLDER


class TestSendStaticEmail(unittest.TestCase):
    def setUp(self):
        self.dummy_pdf = os.path.join(OUTPUT_FOLDER, "XXXXXDXXXXXXXX.pdf")

    def test_send_email_via_postmark_success(self):
        # Call the function to be tested.
        result = send_email_via_postmark(
            sender="loxteam@loxsolution.com",
            receivers=["loxteam@loxsolution.com"],
            template_alias="unit-testing-template",
            attachments=[self.dummy_pdf],
        )

        # Assert the expected response.
        self.assertIsInstance(result, requests.Response)
        self.assertEqual(result.status_code, 200)

    def test_send_email_via_postmark_failure(self):
        template_that_doesnt_exist = "template-that-doesnt-exist"

        # Call the function to be tested.
        result = send_email_via_postmark(
            sender="loxteam@loxsolution.com",
            receivers=["loxteam@loxsolution.com"],
            template_alias=template_that_doesnt_exist,
            attachments=[self.dummy_pdf],
        )

        # Assert the expected response.
        self.assertIsInstance(result, requests.Response)
        self.assertEqual(result.status_code, 422)


if __name__ == "__main__":
    unittest.main()
