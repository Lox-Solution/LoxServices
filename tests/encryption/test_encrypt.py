import os
import unittest
from getpass import getpass

from unittest.mock import patch, MagicMock
from io import StringIO
from base64 import urlsafe_b64encode
from hashlib import scrypt


from lox_services.encryption.encrypt import (
    generate_key,
    load_key,
    encrypt_message,
    decrypt_message,
    replace_injection_keys,
)

FAKE_ENCRYPTION_KEY = "dFcxr0SE8yOWiWntoomu7gBbWQOsVh5kpayhIXl793M="
FAKE_PASSWORD = "password"
FAKE_ENCRYPTED_PASSWORD = "gAAAAABjbi2AIVY6SUmCURFm7JV1dyukZ6EOjopwu1AhJ5ajcDzpfiqmUKjJmc8ncQYuoOz5iko9v1e_106V9u0MAzHcnb7WTA=="

os.environ["ENCRYPTION_KEY"] = FAKE_ENCRYPTION_KEY


class Test_encrypt_functions(unittest.TestCase):
    @patch('getpass.getpass')
    @patch('os.environ')
    def test_generate_key(self, mock_environ, mock_getpass):
        mock_getpass.side_effect = ["password123", "password123", "somesalt", "somesalt"]
        mock_environ.__setitem__ = MagicMock()

        key_encoded = generate_key()

        mock_getpass.assert_called_with("Verify salt:")
        self.assertEqual(mock_getpass.call_count, 4)
        mock_environ.__setitem__.assert_called_once_with("ENCRYPTION_KEY", str(key_encoded))
        self.assertEqual(key_encoded, urlsafe_b64encode(scrypt(
            "password123".encode('utf-8'), salt="somesalt".encode('utf-8'), n=16384, r=8, p=1, dklen=32
        )))

        
    def test_load_key(self):
        self.assertEqual(load_key(), bytes(FAKE_ENCRYPTION_KEY, "UTF-8"))

    def test_encrypt_decrypt_msg(self):
        encrypted_msg = encrypt_message(FAKE_PASSWORD)
        self.assertEqual(
            decrypt_message(encrypted_msg), decrypt_message(FAKE_ENCRYPTED_PASSWORD)
        )


    def test_replace_injection_keys(self):
        # Test message with injection keys
        self.assertEqual(replace_injection_keys("Hello <world>!"), "Hello &ltworld&gt!")

        # Test message with reversed injection keys
        self.assertEqual(
            replace_injection_keys("Hello &ltworld&gt!", True), "Hello <world>!"
        )

        # Test message with multiple injection keys
        self.assertEqual(
            replace_injection_keys(
                'This is a <test> message with & multiple "injection" keys.'
            ),
            "This is a &lttest&gt message with &amp multiple &quotinjection&quot keys.",
        )

        # Test message with reversed multiple injection keys
        self.assertEqual(
            replace_injection_keys(
                "This is a &amplttest&ampgt message with &amp multiple &ampquotinjection&ampquot keys.",
                True,
            ),
            'This is a <test> message with & multiple "injection" keys.',
        )
