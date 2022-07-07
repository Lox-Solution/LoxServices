#pylint: disable=missing-class-docstring missing-function-docstring
import unittest

from lox_services.email.utils import extract_emails_from_string

class Test_extract_emails_from_string(unittest.TestCase):
    
    def test_extract_one_email(self):
        self.assertEqual(extract_emails_from_string("I am an email email@domain.com."), ["email@domain.com"]) 

    def test_string_empty(self):
        self.assertEqual(extract_emails_from_string(""), [])

    def test_extract_no_email(self):
        self.assertEqual(extract_emails_from_string("This is not an email: [email@gmsa^il.com]."), [])
        self.assertEqual(extract_emails_from_string("This is not an email: email@student.tu-delft._com."), [])
        self.assertEqual(extract_emails_from_string("This is not an email: email_email@domain-si"), [])

    def test_extract_special_character_emails(self):
        self.assertEqual(extract_emails_from_string("-Az48.29@NEW-domain.Com."), ["az48.29@new-domain.com"])
        self.assertEqual(extract_emails_from_string("<br>*Recipient@gmail.com<br>"), ["recipient@gmail.com"])
        self.assertEqual(extract_emails_from_string("re--CI_PIENT@my.outlook.fr,"), ["ci_pient@my.outlook.fr"])

    def test_special_character_exception(self):
        self.assertNotEqual(extract_emails_from_string("Special character email: <br>email@gmail.com--<br>."), ["email@gmail.com"])
        
if __name__ == '__main__':
    unittest.main()
