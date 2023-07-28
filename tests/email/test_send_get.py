import os
import unittest
from lox_services.email.send import send_emails_from_loxsolution_account
from lox_services.config.paths import OUTPUT_FOLDER


class TestSend(unittest.TestCase):
    def setUp(self):
        self.sender_email = "loxteam@loxsolution.com"
        self.incorrect_sender_email = "dummy@dummy.com"
        self.receiver_emails = ["loxteam@loxsolution.com"]
        self.cc_email_addresses = ["loxteam@loxsolution.com"]
        self.bcc_email_addresses = ["loxteam@loxsolution.com"]
        self.subject = "Unit Testing LoxServices"
        self.content = "This is a test email sent from the LoxServices unit tests."
        self.pdf_path = os.path.join(OUTPUT_FOLDER, "XXXXXDXXXXXXXX.pdf")

    def test_send_emails(self):
        # Run the function with the test data
        with self.assertRaises(None):
            send_emails_from_loxsolution_account(
                sender_email_address=self.sender_email,
                receiver_email_addresses=self.receiver_emails,
                cc_email_addresses=self.cc_email_addresses,
                bcc_email_addresses=self.bcc_email_addresses,
                subject=self.subject,
                content=self.content,
                attachments=[self.pdf_path],
            )

    def test_invalid_sender_email(self):
        # Run the function with the test data and expect a ValueError
        with self.assertRaises(ValueError):
            send_emails_from_loxsolution_account(
                sender_email_address=self.incorrect_sender_email,
                receiver_email_addresses=self.receiver_emails,
                subject=self.subject,
                content=self.content,
            )


if __name__ == "__main__":
    unittest.main()
