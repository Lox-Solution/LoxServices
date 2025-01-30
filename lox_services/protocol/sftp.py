import paramiko
import socket
import errno
from base64 import decodebytes


def establish_sftp_connection(
    ssh_client, server, port, username, password, keydata=None, key_type=None
):
    """Establishes an SFTP connection to the server.

    ## Arguments:
    - `ssh_client`: The client object.
    - `server`: The server to connect to.
    - `port`: The server port to connect to.
    - `username`: The username to authenticate as.
    - `password`: Used for password authentication.
    - `keydata`: The server's host key (optional).
    - `key_type`: The server's host key type (optional).

    ## Returns:
    - An SFTPClient session object if successful, otherwise None.

    ## Important:
    - Remember to CLOSE the SFTP client when done.

    ## Example:
    ```python
    ssh_client = paramiko.SSHClient()
    server = "test.rebex.net"
    port = 22
    username = "demo"
    password = "password"
    sftp = establish_sftp_connection(ssh_client, server, port, username, password)
    # Use SFTP client
    sftp.close()
    ssh_client.close()
    ```
    """
    try:
        # Always set missing host key policy to auto-accept (safe for testing)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # If keydata and key_type are provided, use them
        if keydata and key_type:
            print("Using provided host key for authentication.")
            key = paramiko.RSAKey(data=decodebytes(keydata))
            ssh_client.get_host_keys().add(server, key_type, key)

        print(f"Connecting to {server}:{port} as {username}...")

        # Connect using username & password (default for Rebex SFTP)
        ssh_client.connect(server, port, username, password, timeout=10)

        print("Connection successfully established!")
        return ssh_client.open_sftp()

    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials.")
    except paramiko.BadHostKeyException as badHostKeyException:
        print(f"Unable to verify server's host key: {badHostKeyException}")
    except socket.error as socketException:
        print(f"Connection failed: {socketException}")

    return None
