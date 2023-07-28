"""
Adapted from:
https://github.com/google/gmail-oauth2-tools/blob/master/python/oauth2.py
https://developers.google.com/identity/protocols/OAuth2

1. Generate and authorize an OAuth2 (generate_oauth2_token)
2. Generate a new access tokens using a refresh token(refresh_token)
3. Generate an OAuth2 string to use for login (access_token)

This setup is for *LOX_TEAM_EMAIL*
"""

import re
from typing import List
import base64
import json
from urllib import request
from urllib import parse

from lox_services.config.env_variables import get_env_variable

GOOGLE_ACCOUNTS_BASE_URL = "https://accounts.google.com"
REDIRECT_URI = "http://localhost"


def get_google_client_id():
    return get_env_variable("EMAILSENDER_GOOGLE_CLIENT_ID")


def get_google_client_secret():
    return get_env_variable("EMAILSENDER_GOOGLE_CLIENT_SECRET")


def _command_to_url(command: str) -> str:
    """
    Constructs a URL by appending the given `command` to a base URL.

    Parameters:
        command (str): The command to be appended to the base URL.

    Returns:
        str: The formatted URL created by combining the `GOOGLE_ACCOUNTS_BASE_URL` and the `command`.

    Example:
        >>> GOOGLE_ACCOUNTS_BASE_URL = "https://accounts.google.com"
        >>> command = "reset_password"
        >>> _command_to_url(command)
        'https://accounts.google.com/reset_password'
    """
    return "%s/%s" % (GOOGLE_ACCOUNTS_BASE_URL, command)


def url_escape(text: str) -> str:
    """Escape special characters in `text` for safe use in a URL.

    Parameters:
        text (str): The text to be escaped for safe use in a URL.

    Returns:
        str: The URL-encoded version of the input `text`.
    """
    return parse.quote(text, safe="~-._")


def url_format_params(params: dict) -> str:
    """
    Formats a dictionary of parameters into a URL-encoded string.

    This function takes a dictionary of parameters and converts them into a
    URL-encoded string, suitable for use as query parameters in a URL.

    Parameters:
        params (dict): A dictionary containing the parameters to be formatted.

    Returns:
        str: The URL-encoded string representation of the input `params`.

    Example:
        >>> params = {'key': 'my_api_key', 'query': 'apple', 'limit': 10}
        >>> url_format_params(params)
        'key=my_api_key&query=apple&limit=10'

    Note:
        This function uses the `urllib.parse.urlencode()` method to convert
        the dictionary into a URL-encoded string. The resulting string consists
        of key-value pairs joined with '&' and keys and values are properly escaped.

    Reference:
        - Python Documentation for urllib.parse.urlencode:
        https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode
    """
    param_fragments = []
    for param in sorted(params.items(), key=lambda x: x[0]):
        param_fragments.append("%s=%s" % (param[0], url_escape(param[1])))
    return "&".join(param_fragments)


def generate_permission_url(client_id, scope="https://mail.google.com/"):
    params = {}
    params["client_id"] = client_id
    params["redirect_uri"] = REDIRECT_URI
    params["scope"] = scope
    params["response_type"] = "code"
    return "%s?%s" % (_command_to_url("o/oauth2/auth"), url_format_params(params))


def call_authorize_tokens(client_id, client_secret, authorization_code):
    params = {}
    params["client_id"] = client_id
    params["client_secret"] = client_secret
    params["code"] = authorization_code
    params["redirect_uri"] = REDIRECT_URI
    params["grant_type"] = "authorization_code"
    request_url = _command_to_url("o/oauth2/token")
    response = (
        request.urlopen(request_url, parse.urlencode(params).encode("UTF-8"))
        .read()
        .decode("UTF-8")
    )
    return json.loads(response)


def call_refresh_token(client_id, client_secret, refresh_token):
    params = {}
    params["client_id"] = client_id
    params["client_secret"] = client_secret
    params["refresh_token"] = refresh_token
    params["grant_type"] = "refresh_token"
    request_url = _command_to_url("o/oauth2/token")
    response = (
        request.urlopen(request_url, parse.urlencode(params).encode("UTF-8"))
        .read()
        .decode("UTF-8")
    )
    return json.loads(response)


def generate_oauth2_string(username, access_token, as_base64=False):
    auth_string = "user=%s\1auth=Bearer %s\1\1" % (username, access_token)
    if as_base64:
        auth_string = base64.b64encode(auth_string.encode("ascii")).decode("ascii")
    return auth_string


def get_authorization(google_client_id, google_client_secret):
    scope = "https://mail.google.com/"
    print(
        "Navigate to the following URL to auth:",
        generate_permission_url(google_client_id, scope),
    )
    authorization_code = input("Enter verification code: ")
    response = call_authorize_tokens(
        google_client_id, google_client_secret, authorization_code
    )
    print(response["scope"], response["expires_in"])
    return response["access_token"]


def refresh_authorization(refresh_token: str) -> str:
    response = call_refresh_token(
        get_google_client_id(), get_google_client_secret(), refresh_token
    )
    return response["access_token"]


def extract_emails_from_string(string: str) -> List[str]:
    """Extracts all emails from a string.
    ## Arguments
    - `string`: The string to extract emails from.

    ## Returns
    - A list of emails if any were found.
    - An empty list if no emails were found.

    ## Examples
    ```
        emails = extract_emails_from_string("My email is alexandre@domain.com")
        print(emails) # ["alexandre@domain.com"]

        no_emails = extract_emails_from_string("This is a string without emails")
        print(no_emails) # []
    ```
    ## Exceptions
    ```
        emails = extract_emails_from_string("email@domain.com--")   # double special character after email
        print(emails) # []
    ```


    """

    return re.findall(
        r"[a-z0-9](?!.*[!#$%&*+-/=?^_`}{|]{2})[a-z0-9!#$%&*+-/=?^_`}{|]{0,62}[a-z0-9]+@[a-z0-9.-]+\.[a-z0-9]+",
        string.lower(),
    )
