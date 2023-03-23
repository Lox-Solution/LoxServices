import paramiko
import errno
import socket
from base64 import decodebytes


def establish_sftp_connection(
    ssh_client, server, port, username, password, keydata, key_type
):
    """Establishes sftp connection to server.
    ## Arguments
    - `ssh_client`: The client object.
    - `server`: The server to connect to.
    - `port`: The server port to connect to.
    - `username`: The username to authenticate as.
    - `password`: Used for password authentication.
    - `keydata` : The server's host key (you can find it with 'ssh-keyscan example.com' command in terminal).
    - `key_type` : The server's host key type (you can find it with keydata).

    ## Returns
    - A new SFTPClient session object.

    ## Important
    - When you are done using the client object don't forget to CLOSE it!!!

    ## Examples
    ```python
    ssh_client = paramiko.SSHClient()
    keydata = b'AAAAAbsbsbs'
    key_type = 'ssh-rsa'
    server = '12.34.56.78'
    port = 22
    username = 'username'
    password = 'password'
    sftp = establish_sftp_connection(ssh_client, server, port, user, password, keydata, key_type)
    # DO STUFF
    ssh_client.close()
    ```
    """
    key = paramiko.RSAKey(data=decodebytes(keydata))
    ssh_client.get_host_keys().add(server, key_type, key)
    try:
        ssh_client.connect(server, port, username, password, timeout=10)
        print("Connection succesfully established … ")
        return ssh_client.open_sftp()
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials: %s")
    except paramiko.BadHostKeyException as badHostKeyException:
        print("Unable to verify server's host key: %s" % badHostKeyException)
    except paramiko.SSHException as sshException:
        print("Unable to establish SSH connection: %s" % sshException)
    except socket.error as v:
        e_code = v[0]
        if e_code == errno.ECONNREFUSED:
            print("Connection Refused")
