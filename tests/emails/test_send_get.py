import os
import random
import shutil
import unittest
from unittest.mock import MagicMock, patch
from lox_services.emails.send import (
    ContentTypes,
    send_emails_from_loxsolution_account,
    send_email,
)
from lox_services.emails.get import get_emails, download_attachments
from tests import OUTPUT_FOLDER
from email.message import Message


class TestSendGet(unittest.TestCase):
    def setUp(self):
        self.output_folder = OUTPUT_FOLDER
        self.temp_output_folder = os.path.join(self.output_folder, "temp")
        self.csv_name = "dummy.csv"
        self.html_name = "dummy.html"
        self.index = random.randint(0, 1000000)
        self.sender_email = "loxteam@loxsolution.com"
        self.incorrect_sender_email = "dummy@dummy.com"
        self.receiver_emails = ["loxteam@loxsolution.com"]
        self.cc_email_addresses = ["loxteam@loxsolution.com"]
        self.bcc_email_addresses = ["loxteam@loxsolution.com"]
        self.subject = "Unit Testing LoxServices"
        self.content = "This is a test email sent from the LoxServices unit tests."
        self.csv_path = os.path.join(self.output_folder, self.csv_name)
        self.html_path = os.path.join(self.output_folder, self.html_name)
        self.expected_subject = f"{self.subject} - {self.index}"
        self.label = "Unittest"
        self.html_content = f"<html><body><h1>{self.content}</h1></body></html>"

        if not os.path.exists(self.temp_output_folder):
            shutil.os.makedirs(self.temp_output_folder)

    def tearDown(self):
        if os.path.exists(self.temp_output_folder):
            shutil.rmtree(self.temp_output_folder)

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        # Mock the SMTP instance and its methods
        smtp_instance = mock_smtp.return_value
        smtp_instance.sendmail.return_value = {}

        # Call the function that sends the email
        result = send_email(
            sender_email_address=self.sender_email,
            sender_smtp_server="smtp.gmail.com",
            sender_password="dummy",
            receiver_email_address=self.receiver_emails[0],
            cc_email_addresses=self.cc_email_addresses,
            bcc_email_addresses=self.bcc_email_addresses,
            subject=self.subject,
            content=self.content,
            attachments=[self.csv_path, self.html_path],
        )

        # Assert that the function returned successfully
        self.assertEqual(result, True)

    @patch("smtplib.SMTP")
    def test_send_email_failure(self, mock_smtp):
        # Mock the SMTP instance and its methods to simulate failure
        smtp_instance = mock_smtp.return_value
        smtp_instance.sendmail.side_effect = Exception("Connection error")

        # Call the function that sends the email
        result = send_email(
            sender_email_address=self.sender_email,
            sender_smtp_server="smtp.gmail.com",
            sender_password="dummy",
            receiver_email_address=self.receiver_emails[0],
            cc_email_addresses=self.cc_email_addresses,
            bcc_email_addresses=self.bcc_email_addresses,
            subject=self.subject,
            content=self.content,
            attachments=[self.csv_path, self.html_path],
        )

        # Assert that the function returned False due to the failure
        self.assertEqual(result, False)

    @patch("smtplib.SMTP")
    def test_send_email_html_content(self, mock_smtp):
        # Mock the SMTP instance and its methods
        smtp_instance = mock_smtp.return_value
        smtp_instance.sendmail.return_value = {}

        # Call the function that sends the email
        result = send_email(
            sender_email_address=self.sender_email,
            sender_smtp_server="smtp.gmail.com",
            sender_password="dummy",
            receiver_email_address=self.receiver_emails[0],
            cc_email_addresses=self.cc_email_addresses,
            bcc_email_addresses=self.bcc_email_addresses,
            subject=self.subject,
            content=self.html_content,
            content_type=ContentTypes.HTML,
            attachments=[self.csv_path, self.html_path],
        )

        # Assert that the function returned successfully
        self.assertEqual(result, True)

    def test_send_get_emails(self):
        send_emails_from_loxsolution_account(
            sender_email_address=self.sender_email,
            receiver_email_addresses=self.receiver_emails,
            cc_email_addresses=self.cc_email_addresses,
            bcc_email_addresses=self.bcc_email_addresses,
            subject=f"{self.subject} - {self.index}",
            content=self.content,
            attachments=[self.csv_path, self.html_path, None],
        )

        emails = get_emails(
            self.label, days=1, search={"subject": self.expected_subject}
        )

        # Assert the results
        self.assertEqual(len(emails), 1)
        self.assertIsInstance(emails[0], Message)
        self.assertEqual(emails[0]["Subject"], self.expected_subject)

        file_names = download_attachments(emails[0], self.temp_output_folder)
        self.assertTrue(self.csv_name in file_names)
        self.assertTrue(self.html_name in file_names)

        # Case 2: Already downloaded file
        # Call the function with mock data
        file_names = download_attachments(emails[0], self.temp_output_folder)

        # Assert the results
        self.assertEqual(len(file_names), 0)

    def test_invalid_sender_email(self):
        # Run the function with the test data and expect a ValueError
        with self.assertRaises(ValueError):
            send_emails_from_loxsolution_account(
                sender_email_address=self.incorrect_sender_email,
                receiver_email_addresses=self.receiver_emails,
                subject=self.subject,
                content=self.content,
            )


class TestGet(unittest.TestCase):
    def setUp(self):
        self.label = "Unittest"

    def test_invalid_label(self):
        with self.assertRaises(ValueError):
            get_emails("wronglabel", days=1)

    def test_no_email(self):
        emails = get_emails(self.label, days=1, search={"subject": "wrongsubject"})
        self.assertEqual(len(emails), 0)

    @patch("imaplib.IMAP4_SSL")
    def test_no_emails_found(self, mock_imaplib):
        # Mock the IMAP4_SSL instance and its methods
        mock_imap_ssl_client = MagicMock()
        mock_imap_ssl_client.select.return_value = ("OK", b"0")  # Mock an empty mailbox

        # Patch the authenticate method to avoid actual authentication
        def mock_authenticate(x, y):
            return True

        mock_imap_ssl_client.authenticate = mock_authenticate

        # Apply the mocked IMAP4_SSL instance
        mock_imaplib.return_value = mock_imap_ssl_client

        # Mock the search method to return an empty result
        mock_imap_ssl_client.search.return_value = ("BAD", [b""])

        # Call the function under test
        result = get_emails("Carriers/Chronopost", 30, search={}, strict=False)

        # Assert the function returns None when no emails are found
        self.assertIsNone(result)
        mock_imap_ssl_client.select.assert_called_once_with("Carriers/Chronopost")
        mock_imap_ssl_client.search.assert_called_once()
        # No fetch calls should be made
        self.assertEqual(mock_imap_ssl_client.fetch.call_count, 0)

    @patch("imaplib.IMAP4_SSL")
    def test_unknown_error_occurred(self, mock_imaplib):
        # Mock the IMAP4_SSL instance and its methods
        mock_imap_ssl_client = MagicMock()
        mock_imap_ssl_client.select.return_value = (
            "OK",
            b"1",
        )  # Mock one email in the mailbox

        # Patch the authenticate method to avoid actual authentication
        def mock_authenticate(x, y):
            return True

        mock_imap_ssl_client.authenticate = mock_authenticate

        # Apply the mocked IMAP4_SSL instance
        mock_imaplib.return_value = mock_imap_ssl_client

        # Mock the search method to return the email
        mock_imap_ssl_client.search.return_value = ("OK", [b"1"])

        # Mock the fetch method to return an error status
        mock_imap_ssl_client.fetch.return_value = ("BAD", [b""])

        # Call the function under test
        with self.assertRaises(Exception) as context:
            get_emails("Carriers/Chronopost", 30, search={}, strict=False)

        # Assert that the function raised an exception with the correct message
        self.assertEqual(
            str(context.exception),
            "An unknown error occured while trying to fetch email body.",
        )


if __name__ == "__main__":
    unittest.main()
