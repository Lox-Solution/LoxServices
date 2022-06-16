#pylint: disable=missing-class-docstring missing-function-docstring
import unittest

from src.email.utils import extract_emails_from_string

class Test_extract_emails_from_string(unittest.TestCase):
    
    def test_extract_one_email(self):
        self.assertEqual(extract_emails_from_string("I am an email email@domain.com."), ["email@domain.com"]) 

    def test_string_empty(self):
        self.assertEqual(extract_emails_from_string(""), [])

    def test_extract_no_email(self):
        self.assertEqual(extract_emails_from_string("This is not an email: [email@gmsa^il.com]."), [])
        self.assertEqual(extract_emails_from_string("This is not an email: email@student.tu-delft._com."), [])
        self.assertEqual(extract_emails_from_string("Not email_email@domain-si"), [])

    def test_extract_special_character_emails(self):
        self.assertEqual(extract_emails_from_string("Special character emails: <br>email@gmail.com-_<br>."), ["email@gmail.com"])
        self.assertEqual(extract_emails_from_string("-Az48.29@NEW-domain.Com."), ["Az48.29@NEW-domain.Com"])
        self.assertEqual(extract_emails_from_string("*Recipient@gmail.com,"), ["Recipient@gmail.com"])
        self.assertEqual(extract_emails_from_string("re--CI_PIENT@my.outlook.fr."), ["CI_PIENT@my.outlook.fr"])
        
if __name__ == '__main__':
    unittest.main()
