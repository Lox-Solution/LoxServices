import unittest
import paramiko
from base64 import encodebytes
from lox_services.protocol.sftp import establish_sftp_connection


class YourModuleTests(unittest.TestCase):
    def setUp(self):
        self.ssh_client = paramiko.SSHClient()
        self.keydata = b"AAAAB3NzaC1yc2EAAAABJQAAAQEAkRM6RxDdi3uAGogR3nsQMpmt43X4WnwgMzs8VkwUCqikewxqk4U7EyUSOUeT3CoUNOtywrkNbH83e6/yQgzc3M8i/eDzYtXaNGcKyLfy3Ci6XOwiLLOx1z2AGvvTXln1RXtve+Tn1RTr1BhXVh2cUYbiuVtTWqbEgErT20n4GWD4wv7FhkDbLXNi8DX07F9v7+jH67i0kyGm+E3rE+SaCMRo3zXE6VO+ijcm9HdVxfltQwOYLfuPXM2t5aUSfa96KJcA0I4RCMzA/8Dl9hXGfbWdbD2hK1ZQ1pLvvpNPPyKKjPZcMpOznprbg+jIlsZMWIHt7mq2OJXSdruhRrGzZw=="
        self.key_type = "ssh-rsa"
        self.server = "test.rebex.net"
        self.port = 22
        self.username = "demo"
        self.password = "password"

    def test_establish_sftp_connection_successful(self):
        sftp = establish_sftp_connection(
            self.ssh_client,
            self.server,
            self.port,
            self.username,
            self.password,
            self.keydata,
            self.key_type,
        )
        self.assertIsInstance(sftp, paramiko.SFTPClient)
        sftp.close()

    def test_establish_sftp_connection_authentication_failure(self):
        self.password = "wrong_password"
        sftp = establish_sftp_connection(
            self.ssh_client,
            self.server,
            self.port,
            self.username,
            "wrong_password",
            self.keydata,
            self.key_type,
        )
        self.assertIsNone(sftp)

    def test_establish_sftp_connection_bad_host_key(self):
        self.keydata = b"AAAAB3NzaC1yc2EAAAADAQABAAABAQCl962sEMWkg3psqnWaxtvIW3ZTCQFqVOyxcexJ9eztOXeW+GG3397lEaKxDcaHuiE8Iw2axG1C00tHZFJGIWGRblXolCQHCxbU5eVFnwCFZVl5K/uUcMeCk7eQx85tZcAotLFyVUBUuCxrecxKgZIqk7V2xx/yjxi3RnBhDPvvOd6glIEfGtkpUcd6eX1oUILGuPL4i3Gx2FW+67LhFKsukaMbhuz1bp/w3e74l495153ULTK85H5TGprLxQA6woc7p8YE8Q4Tkf4Kbz8x7lZgNYSi9Rglj3kghNsfdPGRFZVXOrKMa6rHKCVvfNls0UxhexmslGUup+8ANtWzUXUH"
        sftp = establish_sftp_connection(
            self.ssh_client,
            self.server,
            self.port,
            self.username,
            self.password,
            self.keydata,
            self.key_type,
        )
        self.assertIsNone(sftp)

    def test_establish_sftp_connection_ssh_exception(self):
        sftp = establish_sftp_connection(
            self.ssh_client,
            self.server,
            23,
            self.username,
            self.password,
            self.keydata,
            self.key_type,
        )
        self.assertIsNone(sftp)

    def tearDown(self):
        self.ssh_client.close()


if __name__ == "__main__":
    unittest.main()
