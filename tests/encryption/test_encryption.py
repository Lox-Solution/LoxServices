import os
import unittest


from lox_services.encryption.encrypt import (
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
