#pylint: disable=missing-class-docstring missing-function-docstring
import unittest

from src.email.utils import extract_emails_from_string

class Test_extract_emails_from_string(unittest.TestCase):
    
    def test_extract_one_email(self):
        self.assertEqual(extract_emails_from_string("I am an email email@domain.com."), ["email@domain.com"]) #dsoihfqshgghqdfiufhsdiuosdfhusikdfghsudf
        
    def test_string_empty(self):
        self.assertEqual(extract_emails_from_string(""), [])
        
if __name__ == '__main__':
    unittest.main()
