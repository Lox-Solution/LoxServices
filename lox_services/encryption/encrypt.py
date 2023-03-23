"""All configured encryption functions."""
import getpass
import os
from base64 import urlsafe_b64encode
from hashlib import scrypt

import pandas as pd
from cryptography.fernet import Fernet

from lox_services.config.env_variables import get_env_variable
from lox_services.utils.general_python import print_error


# generate a new, not in the same file than the old one
def generate_key() -> None:
    """Generates a key from password and salt and adds it in env variables."""
    password = getpass.getpass("Password:")
    verify_password = getpass.getpass("Verify password:")
    if password != verify_password:
        raise Exception("Passwords must be equals")

    salt = getpass.getpass("Salt:")
    verify_salt = getpass.getpass("Verify salt:")
    if salt != verify_salt:
        raise Exception("Salts must be equals")

    key = scrypt(
        password.encode("utf-8"), salt=salt.encode("utf-8"), n=16384, r=8, p=1, dklen=32
    )
    key_encoded = urlsafe_b64encode(key)
    os.environ["ENCRYPTION_KEY"] = str(key_encoded)
    return key_encoded


def load_key() -> bytes:
    """Loads the secret key."""
    try:
        string_encryption_key = get_env_variable("ENCRYPTION_KEY")
        return bytes(string_encryption_key, encoding="utf-8")
    except KeyError as keyError:
        print_error(
            "No encryption key found in the environment variables, please check your .env file or use generate_key function with pwd and salt."
        )
        raise keyError


def encrypt_message(message: str):
    """Encrypts a string with the secret key.
    ## Arguments
    - `message`: The string to encrypt.

    ## Returns
    The encrypted message as a string.
    """
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message.decode()


def decrypt_message(encrypted_message):
    """Decrypt the encrypted string with the secret key.
    ## Arguments
    - `encrypted_message`: The string to decrypt.

    ## Returns
    The message as a string.
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message.encode())

    return decrypted_message.decode()
